default: run

.PHONY: run test push transcode

run:
	@cd app/ && python server.py 80

test:
	@cd test/server/ && python alltests.py

push:
	@cd app/ && python worker_push_notification.py

transcode:
	@cd app/ && python worker_transcode.py
