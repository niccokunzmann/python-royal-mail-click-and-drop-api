
.PHONY: stubs api-definition stubs-help image

#
# Download the API definition file
#
api-definition:
	wget -O click-and-drop-api-v1.yaml https://api.parcel.royalmail.com/doc/v1/click-and-drop-api-v1.yaml

image:
	docker pull openapitools/openapi-generator-cli


#
# Generate the source code
#
stubs: image
	docker run --rm -v "$${PWD}:/local" -u $$(id -u):$$(id -g) openapitools/openapi-generator-cli generate \
		-i /local/click-and-drop-api-v1.yaml \
		-g python \
		-o /local/ \
		--package-name click_and_drop_api \
		--git-host https://github.com \
		--git-user-id niccokunzmann \
		--git-repo-id python-royal-mail-click-and-drop-api \
		--minimal-update \
		--server-variables "host=api.parcel.royalmail.com"
	make fix-stubs
# 	sudo chown -R $(id -u):$(id -g) .

stubs-help: image
	docker run --rm openapitools/openapi-generator-cli help generate	

.venv:
	python3 -m venv .venv
	.venv/bin/pip install --upgrade "pip>=25.1"
	.venv/bin/pip install --group dev -e .

.PHONY: html livehtml fix-stubs github-pages

fix-stubs:
	for f in docs/*.md; do \
		sed -i "s|../README.md|api.md|g" $$f; \
	done
	mv README.md docs/api.md
	sed -i "s|docs/|./|g" docs/api.md
	sed -i "s|(#installation--usage)||g" docs/api.md
	sed -i "s|\[default to 25\]|default to 25|g" docs/OrdersApi.md
	git checkout -- .gitignore
	git checkout -- README.md || true

html: .venv
	.venv/bin/mkdocs build

livehtml: .venv
	.venv/bin/mkdocs serve

github-pages: .venv
	.venv/bin/mkdocs gh-deploy --force

.PHONY: test-examples

# run all examples
# respect rate limit
# > Exceeding the rate limit of 5 calls per second will result in a 429 error.
test-examples: .venv
	for f in examples/*.py; do \
		echo $$f; \
		.venv/bin/python $$f || exit 1; \
		echo; \
		sleep 1; \
	done