// VPC + Subnets

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
}

resource "aws_subnet" "public_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
  map_public_ip_on_launch = true
  availability_zone = "${var.aws_region}a"
}

resource "aws_subnet" "public_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.2.0/24"
  map_public_ip_on_launch = true
  availability_zone = "${var.aws_region}b"
}

resource "aws_subnet" "private_1" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.11.0/24"
  availability_zone = "${var.aws_region}a"
}

resource "aws_subnet" "private_2" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.12.0/24"
  availability_zone = "${var.aws_region}b"
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
}

resource "aws_route_table" "public_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
}

resource "aws_route_table_association" "public_1_assoc" {
  subnet_id      = aws_subnet.public_1.id
  route_table_id = aws_route_table.public_rt.id
}

resource "aws_route_table_association" "public_2_assoc" {
  subnet_id      = aws_subnet.public_2.id
  route_table_id = aws_route_table.public_rt.id
}

//Config ECS
resource "aws_security_group" "ecs_sg" {
  name   = "${var.project_name}-ecs-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    security_groups = [aws_security_group.alb_sg.id]  # o 0.0.0.0/0 si quieres abierto
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

}

resource "aws_security_group" "alb_sg" {
  name   = "${var.project_name}-alb-sg"
  vpc_id = aws_vpc.main.id

  # Permitir HTTP desde internet
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


//Config RDS
resource "aws_security_group" "rds_sg" {
  name   = "${var.project_name}-rds-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "Postgres access"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    security_groups = [aws_security_group.ecs_sg.id]
  }
}


//RDS Postgres
resource "aws_db_subnet_group" "db_subnets" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = [aws_subnet.private_1.id, aws_subnet.private_2.id]
}

resource "aws_db_instance" "postgres" {
  identifier = "${var.project_name}-postgres"
  engine     = "postgres"
  instance_class = "db.t3.micro"
  allocated_storage = 20

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name    = aws_db_subnet_group.db_subnets.name
  vpc_security_group_ids  = [aws_security_group.rds_sg.id]
  publicly_accessible     = false
  skip_final_snapshot     = true
}


//ECR Repo
resource "aws_ecr_repository" "repo" {
  name = "${var.project_name}-api"
}

//Cluster Fargate
resource "aws_ecs_cluster" "cluster" {
  name = "${var.project_name}-cluster"
}

//Load Balancer
resource "aws_lb" "alb" {
  name               = "${var.project_name}-alb"
  load_balancer_type = "application"
  subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
  security_groups    = [aws_security_group.alb_sg.id]
}

//Target group
resource "aws_lb_target_group" "tg" {
  name     = "${var.project_name}-tg"
  protocol = "HTTP"
  port     = 8000
  vpc_id   = aws_vpc.main.id

  target_type = "ip"
  health_check {
    path = "/"
    port = "traffic-port"
    protocol = "HTTP"
    healthy_threshold   = 2
    unhealthy_threshold = 3
    interval            = 20
    timeout             = 5
  }
  lifecycle {
    prevent_destroy = true
  }
}


//Listener
resource "aws_lb_listener" "listener" {
  load_balancer_arn = aws_lb.alb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type = "forward"
    target_group_arn = aws_lb_target_group.tg.arn
  }
}

//CloudWatch
resource "aws_cloudwatch_log_group" "ecs_log_group" {
  name              = "/ecs/${var.project_name}"
  retention_in_days = 14
}

//Task Definition para Django
resource "aws_ecs_task_definition" "task" {
  family                   = "${var.project_name}-task"
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "256"
  memory                   = "512"

  container_definitions = jsonencode([
    {
      name  = "django"
      image = "${aws_ecr_repository.repo.repository_url}:${var.image_tag}"
      essential = true
      portMappings = [{ containerPort = 8000, protocol = "tcp"  }]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.ecs_log_group.name
          "awslogs-region"        = var.aws_region
          "awslogs-stream-prefix" = "django"
        }
      }

      environment = [
        { name = "DATABASE_HOST", value = aws_db_instance.postgres.address },
        { name = "DATABASE_NAME", value = var.db_name },
        { name = "DATABASE_USER", value = var.db_username },
        { name = "DATABASE_PASSWORD", value = var.db_password },
      ]
    }
  ])

  execution_role_arn = aws_iam_role.ecs_task_execution.arn

}

//ECS Service 
resource "aws_ecs_service" "service" {
  name            = "${var.project_name}-service"
  cluster         = aws_ecs_cluster.cluster.id
  task_definition = aws_ecs_task_definition.task.arn
  desired_count   = 1
  launch_type     = "FARGATE"

  force_new_deployment = true
  health_check_grace_period_seconds = 60

  network_configuration {
    subnets         = [aws_subnet.private_1.id, aws_subnet.private_2.id]
    security_groups = [aws_security_group.ecs_sg.id]
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.tg.arn
    container_name   = "django"
    container_port   = 8000
  }
  # Asegura el orden de creación/borrado
  depends_on = [
    aws_lb_listener.listener,
    aws_lb.alb,
    aws_lb_target_group.tg
  ]
}


//IAM
resource "aws_iam_role" "ecs_task_execution" {
  name = "${var.project_name}-ecs-task-execution-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ecs-tasks.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "ecs_task_execution_policy" {
  role       = aws_iam_role.ecs_task_execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}


# Elastic IP para el NAT
resource "aws_eip" "nat" {
  domain = "vpc"
}

# NAT Gateway en subnet pública 1
resource "aws_nat_gateway" "nat" {
  allocation_id = aws_eip.nat.id
  subnet_id     = aws_subnet.public_1.id
}

# Route table para subnets privadas
resource "aws_route_table" "private_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat.id
  }
}

# Asociar subnets privadas a la route table
resource "aws_route_table_association" "private_1_assoc" {
  subnet_id      = aws_subnet.private_1.id
  route_table_id = aws_route_table.private_rt.id
}

resource "aws_route_table_association" "private_2_assoc" {
  subnet_id      = aws_subnet.private_2.id
  route_table_id = aws_route_table.private_rt.id
}


