# Volume EBS para ChromaDB
resource "aws_ebs_volume" "chroma_volume" {
  availability_zone = aws_instance.sprint7_instance.availability_zone
  size              = 5  # GB
  type              = "gp3"

  tags = {
    Name = "chroma-db-volume"
  }
}

# Anexar volume à instância EC2
resource "aws_volume_attachment" "chroma_attachment" {
  device_name = "/dev/sdf"
  volume_id   = aws_ebs_volume.chroma_volume.id
  instance_id = aws_instance.sprint7_instance.id
}
