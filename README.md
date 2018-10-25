# Setup

## AWS

### Instance Creation

Create an instance using `docker-machine`:

```bash
$ docker-machine -D create --driver amazonec2 \
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
	awsopt
```

The `create` usually fails and docker doesn't load correctly:

```bash
$ docker-machine stop awsopt
$ docker-machine start awsopt
$ docker-machine regenerate-certs awsopt
```

Check instance State:

```bash
$ docker-machine ip awsopt
$ docker-machine inspect awsopt
```

SSH in:

```bash
$ docker-machine ssh awsopt
```

Update the OS just in case:

```bash
$ sudo apt install --upgrade apt
$ sudo do-release-upgrade -y
```

Because the docker daemon doesn't start sometimes:

```bash
$ sudo nohup docker daemon -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock &
```

### Update Code and Data

Using GitHub repo:

```bash
$ git clone <dicsopt repo addr>
```

An alternative is to use sync data using `rsync` **from the local machine** to the AWS instance:

```bash
# dry run
rsync --dry-run --out-format="[%t]:%o:%f:Last Modified %M" -avrh -e "ssh -i /Users/cavagnolo/.docker/machine/machines/awsopt/id_rsa" ubuntu@ec2-34-204-12-78.compute-1.amazonaws.com:/home/ubuntu/discopt/ .

# pull
rsync -avrh -e "ssh -i /Users/cavagnolo/.docker/machine/machines/awsopt/id_rsa" ubuntu@ec2-34-204-12-78.compute-1.amazonaws.com:/home/ubuntu/discopt/ .

# push
rsync -avrh -e "ssh -i /Users/cavagnolo/.docker/machine/machines/awsopt/id_rsa" . ubuntu@ec2-34-204-12-78.compute-1.amazonaws.com:/home/ubuntu/discopt/
```

Another alternative is to copy data using `scp` **from the local machine** to the AWS instance:

```bash
$ cd ~/learnings/coursera_discopt/
$ docker-machine scp -r . awsopt:
```

## Local

Set some environment variables (TODO: add this to dockerfile):

```bash
$ eval `docker-machine env awsopt`
$ setenv NV_HOST "ssh://ubuntu@`docker-machine ip awsopt`:"
$ ssh-add ~/.docker/machine/machines/awsopt/id_rsa
```

# Usage

## Access Jupyter

```bash
$ docker run \
	-it --rm \
	-p 8888:8888 \
	-v /home/ubuntu:/notebooks \
	-w /notebooks \
	-e PASSWORD='abc123' \
	kcavagnolo/docker_opt
```

# Maintenance

## Docker Image

```bash
$ cd ~/docker/docker_opt
$ export DOCKER_OPT_VER=`git rev-parse --short HEAD`
$ docker build --build-arg VCS_REF=$DOCKER_OPT_VER \
               --build-arg BUILD_DATE=`date -u +”%Y-%m-%dT%H:%M:%SZ”` \
               -t kcavagnolo/docker_opt:$DOCKER_OPT_VER \
               -f Dockerfile .
$ docker login -u $DOCKER_REG_UNAME -p $DOCKER_REG_PSWD
$ docker push kcavagnolo/docker_opt:$DOCKER_OPT_VER
```

## AWS Clean-up

```bash
$ docker stop $(docker ps -a -q)
$ docker rm $(docker ps -a -q)
$ docker rmi $(docker images -a -q)
$ docker-machine stop awsopt
$ docker-machine rm -f awsopt
```
