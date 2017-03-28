# build docker instance
docker-machine -D create --driver amazonec2 \
--amazonec2-instance-type c4.2xlarge \
--amazonec2-ami ami-2c57433b \
--amazonec2-device-name "/dev/sda1" \
--amazonec2-root-size "60" \
--amazonec2-volume-type "gp2" \
--amazonec2-region us-east-1 \
--amazonec2-zone c \
--amazonec2-retries 50 \
--amazonec2-security-group docker-machine \
--amazonec2-vpc-id $AWS_VPC_ID \
--amazonec2-access-key $AWS_ACCESS_KEY_ID \
--amazonec2-secret-key $AWS_SECRET_ACCESS_KEY \
awsopt

# the create usually fails and docker doesn't load correctly
docker-machine stop awsopt
docker-machine start awsopt
docker-machine regenerate-certs awsopt

# check on instance
docker-machine ip awsopt
docker-machine inspect awsopt

# SSH into the machine
docker-machine ssh awsopt

# bc the daemon doesn't start sometimes
sudo nohup docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &

# set env
eval `docker-machine env awsopt`
setenv NV_HOST "ssh://ubuntu@`docker-machine ip awsopt`:"
ssh-add ~/.docker/machine/machines/awsopt/id_rsa

# load local data
docker-machine scp -r . awsopt:

# build image
docker build -t kcavagnolo/docker_opt:latest -f Dockerfile .

# push to repo
docker login
docker push kcavagnolo/docker_opt:latest

# setup notebook
docker run \
 -it --rm \
 -p 8888:8888 \
 -v /home/ubuntu:/notebooks \
 -w /notebooks \
 -e PASSWORD='abc123' \
 kcavagnolo/docker_opt

# clean-up
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)

# close and kill instance
docker rmi $(docker images -a -q)
docker-machine stop awsopt
docker-machine rm -f awsopt
