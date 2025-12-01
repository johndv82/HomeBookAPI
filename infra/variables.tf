variable "aws_region" { type = string }
variable "project_name" { type = string }
variable "db_username" { type = string }
variable "db_password" { type = string }
variable "db_name" { type = string }
variable "image_tag" {
  type = string
}


variable "django_superuser_password" { type = string }
variable "django_superuser_email" { type = string }
variable "django_superuser_username" { type = string }