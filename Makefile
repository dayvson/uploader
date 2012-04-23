default: run

.PHONY: run test push transcode jasmine

run:
	@cd app/ && python server.py 80

test:
	@cd test/server/ && python uploader.py

push:
	@cd app/ && python worker_push_notification.py

transcode:
	@cd app/ && python worker_transcode.py

jasmine:
	@cd test/javascript && python jasmine_runner.py