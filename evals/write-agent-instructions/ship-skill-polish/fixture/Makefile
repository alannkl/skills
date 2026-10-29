.PHONY: release smoke

release:
	docker build -t registry.example.com/api:$$(git describe --tags) .
	docker push registry.example.com/api:$$(git describe --tags)

smoke:
	curl -fsS "https://$(ENV).api.example.com/health" && curl -fsS "https://$(ENV).api.example.com/v1/status"
