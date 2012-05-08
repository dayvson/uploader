default: run

.PHONY: run test push transcode

run:
	@cd app/ && python server.py

test:
	@cd test/server/ && python alltests.py
