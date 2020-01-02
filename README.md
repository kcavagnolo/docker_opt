# README

## Intro

This repo contains code and instructions for launching an AWS EC2 instance using a Docker container designed for programming in discrete optimization projects. Docker Machine is used to [manage the instance](https://docs.docker.com/machine/examples/aws/) and uses a [pre-built image](https://hub.docker.com/r/kcavagnolo/docker_opt/) hosted on Docker Hub.

## Setup

The setup steps below assume that the environment variables `AWS_VPC_ID`, `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set on the local machine.

Create an instance using `docker-machine`:

```bash
docker-machine -D create \
    --driver amazonec2 \
    --amazonec2-instance-type c4.2xlarge \
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
    aws-ec2-opt
```

Check instance state:

```bash
docker-machine ip aws-ec2-opt
docker-machine inspect aws-ec2-opt
```

Set some environment variables (TODO: add this to the `dockerfile`):

```bash
eval $(docker-machine env aws-ec2-opt)
export AWS_EC2_OPT_IPADDR=`docker-machine ip aws-ec2-opt`
setenv NV_HOST "ssh://ubuntu@`docker-machine ip aws-ec2-opt`:"
ssh-add $HOME/.docker/machine/machines/aws-ec2-opt/id_rsa
```

## Usage

### General Development

Using GitHub repo:

```bash
docker-machine ssh aws-ec2-opt
cd ~
git clone git@github.com:kcavagnolo/discopt.git
cd discopt

<do stuff>
```

An alternative is to use sync data using `rsync` **from the local machine** to the AWS instance:

```bash
# dry run
rsync --dry-run \
    --out-format="[%t]:%o:%f:Last Modified %M" \
    -avrh \
    -e "ssh -i $HOME/.docker/machine/machines/aws-ec2-opt/id_rsa" \
    ubuntu@$AWS_EC2_OPT_IPADDR:/home/ubuntu/discopt/ .

# pull from AWS (ubuntu@...) to local (.)
rsync -avrh \
    -e "ssh -i $HOME/.docker/machine/machines/aws-ec2-opt/id_rsa" \
    ubuntu@$AWS_EC2_OPT_IPADDR:/home/ubuntu/data/ \
    .

# push from local (.) to AWS (ubuntu@...)
rsync -avrh \
    -e "ssh -i $HOME/.docker/machine/machines/aws-ec2-opt/id_rsa" \
    . \
    ubuntu@$AWS_EC2_OPT_IPADDR:/home/ubuntu/data/
```

Another alternative is to copy data using `scp` **from the local machine** to the AWS instance:

```bash
cd $HOME/learnings/discopt/
docker-machine scp -r . aws-ec2-opt:/home/ubuntu/discopt/
```

### Jupyter Notebook

```bash
docker run \
    -it --rm \
    -p 8888:8888 \
    -v /home/ubuntu:/notebooks \
    -w /notebooks \
    -e PASSWORD='abc123' \
    kcavagnolo/docker_opt
```

## Maintenance

### Build Docker Image

There is a webhook from GitHub to Docker Hub, so when a `push` onto `origin master` occurs, an automatic build is kicked-off. The below is for versioning if desired:

```bash
cd ~/docker/docker_opt
export DOCKER_OPT_VER=`git rev-parse --short HEAD`
docker build --build-arg VCS_REF=$DOCKER_OPT_VER \
    --build-arg BUILD_DATE=`date -u +”%Y-%m-%dT%H:%M:%SZ”` \
    -t kcavagnolo/docker_opt:$DOCKER_OPT_VER \
    -f Dockerfile .
docker login -u $DOCKER_REG_UNAME -p $DOCKER_REG_PSWD
docker push kcavagnolo/docker_opt:$DOCKER_OPT_VER
```

### AWS Clean-up

> For want is nexte to waste, and shame doeth synne ensue

The paradise of dainty devices. Richard Edwardes

```bash
docker stop $(docker ps -a -q)
docker rm $(docker ps -a -q)
docker rmi $(docker images -a -q)
docker-machine stop aws-ec2-opt
docker-machine rm -f aws-ec2-opt
```

## Known Issues

### Creation Errors

Sometimes `create` fails and Docker doesn't load correctly and leaves behind cert files which can muck-up creating a new instance of the same name:

```bash
docker-machine stop aws-ec2-opt
docker-machine start aws-ec2-opt
docker-machine regenerate-certs aws-ec2-opt
```

### OS Errors

If there are OS errors or other oddities, try troubleshooting directly on the machine:

```bash
docker-machine ssh aws-ec2-opt
sudo apt install --upgrade apt
sudo do-release-upgrade -y
```

Because the docker daemon doesn't start sometimes:

```bash
sudo nohup docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &
```
