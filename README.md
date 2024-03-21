# hack24


# info

region - eu-central-1  
aws account name - 064310218222  

## login aws cli
aws ecr get-login-password | docker login --username AWS --password-stdin 064310218222.dkr.ecr.eu-central-1.amazonaws.com  
aws ecr create-repository --repository-name natelai-backend --region eu-central-1

## docker build and run
docker build -t natelai-backend .  
docker run -d --name natelai-backend -p 8000:80 natelai-backend  

## docker deploy
docker tag natelai-backend:latest 064310218222.dkr.ecr.eu-central-1.amazonaws.com/natelai-backend:latest  
docker push 064310218222.dkr.ecr.eu-central-1.amazonaws.com/natelai-backend:latest  

## AWS elasticbeanstalk
aws elasticbeanstalk create-application --application-name natelai-backend
aws elasticbeanstalk create-environment --application-name natelai-backend --environment-name natelai-backend-env --version-label latest --solution-stack-name "64bit Amazon Linux 2023 v4.2.2 running Docker"