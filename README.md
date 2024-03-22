# hack24


# info

region - eu-central-1  
aws account name - 064310218222  

## login aws cli
aws ecr get-login-password | docker login --username AWS --password-stdin 064310218222.dkr.ecr.eu-central-1.amazonaws.com  
aws ecr create-repository --repository-name natelai-backend --region eu-central-1

## docker build and run
docker build -t natelai-backend .  
docker run -it --rm --name natelai-backend -p 8000:80 natelai-backend  

## docker deploy
docker tag natelai-backend:latest 064310218222.dkr.ecr.eu-central-1.amazonaws.com/natelai-backend:latest  
docker push 064310218222.dkr.ecr.eu-central-1.amazonaws.com/natelai-backend:latest  

## AWS elasticbeanstalk
aws elasticbeanstalk create-application --application-name natelai-backend


## Stuff to work on
[] Include organization specific info in the rerouting voice (e.g. telephone num, organization)
[] Test how well the re-routing
[] Send the summary message
[] Professional enging of the call

[] Pitch
[] Video recording
