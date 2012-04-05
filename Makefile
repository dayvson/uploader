default: run

.PHONY: run test

run:
	@cd app/ && python server.py 80

test:
	@cd test/server/ && python uploader.py
