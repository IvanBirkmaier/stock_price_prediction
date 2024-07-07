.PHONY: dockerstart
dockerstart:
	docker build -t webserver .
	docker run -p 8081:8081 webserver:latest
