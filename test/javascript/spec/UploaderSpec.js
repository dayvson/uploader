describe("Uploader", function() {
  function getBody(){
    return document.getElementsByTagName("body")[0];
  }

  var _uploader;
  beforeEach(function(){
    this.server = new MockHttpServer();
  	this.server.start(); 
  	var form = Util.create("form", {"id":"form_test"});  			
  	var input = Util.create("input", {"type":"file", "name":"datafile", "id":"datafile"});
  	form.appendChild(input);
  	_uploader = new Uploader(form, input, "/progress", "/uploader");
  });
  
  afterEach(function(){
  	this.server.stop();	
  });
  
  it("should be show complete upload, mocking request/response XHR", function(){
  	var response_upload = "/download?uploadKey=123";
  	this.server.handle = function (request) {
		    request.setResponseHeader("Content-Type", "text/html");
		    request.receive(200, response_upload);
		};
 		_uploader.onComplete = function(msg){
 		  expect(msg).toBe(response_upload);
 		}
 		_uploader.start();

  });
  
  it("should be show a error during upload, mocking resquest and abort connection", function(){
  	this.server.handle = function (request) {
		    request.err();
		};
 		spyOn(_uploader, "onError");
 		_uploader.start(); 		
 		expect(_uploader.onError).toHaveBeenCalled();
  });
  
  it("upload should be cancelled when there has been no increase\
    in upload progress for 10 consecutive seconds", function(){
  	jasmine.Clock.useMock();	
 		spyOn(_uploader, "onError");
 		_uploader.start();
 		jasmine.Clock.tick( 10000 );
		expect(_uploader.onError ).toHaveBeenCalled();
      
  });  
  it("should be execute onError after 20 seconds, and receive the save progress", function(){
  	jasmine.Clock.useMock();	
 		spyOn(_uploader, "onError");
 		_uploader.start();
		_uploader.setProgress({loaded:100, total:1000});
		jasmine.Clock.tick( 5000 );
		_uploader.setProgress({loaded:100, total:1000});
 		jasmine.Clock.tick( 20000 );
		expect( _uploader.onError ).toHaveBeenCalled();
      
  })
  
  it ("should show status to finished when upload reaches 100%", function () {   
    var response_upload = "/download?uploadKey=1234";
  	this.server.handle = function (request) {
		    request.setResponseHeader("Content-Type", "text/html");
		    request.receive(200, response_upload);
		}; 
    var prgs = {loaded:1000, total:1000};

    _uploader.onProgress = function(bytesLoaded, bytesTotal, perc){
      expect(bytesLoaded).toBe(prgs.loaded);
      expect(bytesTotal).toBe(prgs.total);
      expect(perc).toBe(100);
    }
    _uploader.onComplete = function(msg){
      expect (_uploader.isUploadComplete()).toBeTruthy();
      expect(msg).toBe(response_upload);
    };
    _uploader.start();
    _uploader.setProgress(prgs.loaded, prgs.total);    
  });

});
