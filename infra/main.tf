// VPC + Subnets

resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "${var.project_name}-vpc" }
}

resource "aws_internet_gateway" "igw" {
  vpc_id = aws_vpc.main.id
  tags   = { Name = "${var.project_name}-igw" }
}

resource "aws_subnet" "public" {
  count = 2
  vpc_id = aws_vpc.main.id
  cidr_block = element(["10.0.1.0/24","10.0.2.0/24"], count.index)
  map_public_ip_on_launch = true
  availability_zone = "${var.aws_region}${element(["a","b"], count.index)}"
  tags = { Name = "${var.project_name}-public-${count.index+1}" }
}

resource "aws_subnet" "private" {
  count = 2
  vpc_id = aws_vpc.main.id
  cidr_block = element(["10.0.11.0/24","10.0.12.0/24"], count.index)
  availability_zone = "${var.aws_region}${element(["a","b"], count.index)}"
  tags = { Name = "${var.project_name}-private-${count.index+1}" }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.igw.id
  }
  tags = { Name = "${var.project_name}-public-rt" }
}

resource "aws_route_table_association" "pub_assoc" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}




//Config ECS
resource "aws_security_group" "ecs_sg" {
  name   = "${var.project_name}-ecs-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    from_port       = 8000
    to_port         = 8000
    protocol        = "tcp"
    cidr_blocks  = ["0.0.0.0/0"] #[aws_security_group.alb_sg.id] 
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

  # Conexión desde ECS
  ingress {
    description      = "Postgres access from ECS"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    security_groups  = [aws_security_group.ecs_sg.id]
  }

  # Conexión desde Bastion Host
  ingress {
    description      = "Postgres access from Bastion"
    from_port        = 5432
    to_port          = 5432
    protocol         = "tcp"
    security_groups  = [aws_security_group.bastion_sg.id] 
  }

  # Conexión desde tu PC (opcional)
  ingress {
    description = "Postgres access from my PC"
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["181.224.38.25/32"] # reemplaza TU_IP
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}


//RDS Postgres
resource "aws_db_subnet_group" "db_subnets" {
  name       = "${var.project_name}-db-subnets"
  subnet_ids = aws_subnet.private[*].id
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
  force_delete = true
}

//Cluster Fargate
resource "aws_ecs_cluster" "cluster" {
  name = "${var.project_name}-cluster"
}

# //Load Balancer
# resource "aws_lb" "alb" {
#   name               = "${var.project_name}-alb"
#   load_balancer_type = "application"
#   subnets            = [aws_subnet.public_1.id, aws_subnet.public_2.id]
#   security_groups    = [aws_security_group.alb_sg.id]
# }

# //Target group
# resource "aws_lb_target_group" "tg" {
#   name     = "${var.project_name}-tg"
#   protocol = "HTTP"
#   port     = 8000
#   vpc_id   = aws_vpc.main.id

#   target_type = "ip"
#   health_check {
#     path = "/"
#     port = "traffic-port"
#     protocol = "HTTP"
#     healthy_threshold   = 2
#     unhealthy_threshold = 3
#     interval            = 20
#     timeout             = 5
#   }
# }


# //Listener
# resource "aws_lb_listener" "listener" {
#   load_balancer_arn = aws_lb.alb.arn
#   port              = 80
#   protocol          = "HTTP"

#   default_action {
#     type = "forward"
#     target_group_arn = aws_lb_target_group.tg.arn
#   }
# }

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
        { name = "DJANGO_SUPERUSER_USERNAME", value = var.django_superuser_username},
        { name = "DJANGO_SUPERUSER_EMAIL", value = var.django_superuser_email},
        { name = "DJANGO_SUPERUSER_PASSWORD", value = var.django_superuser_password},
        { name = "ALLOWED_HOSTS", value = "*" },
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

  network_configuration {
    subnets          = aws_subnet.public[*].id
    security_groups  = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  # load_balancer {
  #   target_group_arn = aws_lb_target_group.tg.arn
  #   container_name   = "django"
  #   container_port   = 8000
  # }
  # # Asegura el orden de creación/borrado
  # depends_on = [
  #   aws_lb_listener.listener,
  #   aws_lb.alb,
  #   aws_lb_target_group.tg
  # ]
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


resource "aws_security_group" "bastion_sg" {
  name   = "${var.project_name}-bastion-sg"
  vpc_id = aws_vpc.main.id

  ingress {
    description = "SSH from my PC"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["181.224.38.25/32"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}