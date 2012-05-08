(function(doc, win){
  /* Only a simple function with callbacks for complete/error/start/progress */
  var BaseUploader = function(){};
  BaseUploader.prototype = {
    onProgress:function(){},
    onComplete:function(){},
    onCancel:function(){},
    onError:function(){},
    onStart:function(){}
  }
  /* This class will make a uploader XHR Level 2 */
  var XHRUploader = function(input, form, urlPost, urlProgress){
    this.inputFile = input;
    this.urlpost = urlPost;
    this.urlprogress = urlProgress;
    this.isUploadComplete = false;
    this.progress = null;
    this.form = form;
  }
  XHRUploader.prototype = new BaseUploader();
  XHRUploader.prototype.start = function(){
    var fd = new FormData();
    var file = this.inputFile.files[0];
    fd.append(this.inputFile.name, file);
    var xhr = this.xhr = new XMLHttpRequest();
    if(xhr.upload)Util.addEvent(xhr.upload, "progress", this._uploadProgress, this);
    Util.addEvent(xhr, "load", this._uploadComplete, this);
    Util.addEvent(xhr, "error", this._uploadFailed, this);
    Util.addEvent(xhr, "abort", this._uploadCanceled, this);
    xhr.open("POST", this.urlPost);
    xhr.send(fd);
    this.isUploadComplete = false;
    this._startVerifyProgress( null );
    this.onStart();
  }
  XHRUploader.prototype.setProgress = function(loaded, total){
    var progressTemp  = {lengthComputable:true, loaded:loaded, total:total};
    this._uploadProgress(progressTemp);
  }
  XHRUploader.prototype._uploadComplete = function(evt){
    this.isUploadComplete = true;
    this.onComplete(this.xhr.responseText);
    clearTimeout(this.checkProgresstimeInterval);
  }
  XHRUploader.prototype._uploadFailed = function(evt){
    this.isUploadComplete = false;
    this.onError();
    clearTimeout(this.checkProgresstimeInterval);
  }
  XHRUploader.prototype._uploadCanceled = function(evt){
    this.isUploadComplete = false;
    this.onCancel();
    clearTimeout(this.checkProgresstimeInterval);
  }
  XHRUploader.prototype._uploadProgress = function(evt){
    if (evt.lengthComputable) {
      var percent = Math.round(evt.loaded / evt.total * 100);
      this.onProgress(evt.loaded, evt.total, percent);
      this._startVerifyProgress( evt.loaded );
    }
  }
  XHRUploader.prototype._startVerifyProgress = function( progress ){
  	clearTimeout(this.checkProgresstimeInterval);
  	var self = this;
    this.checkProgresstimeInterval = setTimeout(function( scope ){
          self._verifyProgress( progress );
    }, 10000, this);
  }
  XHRUploader.prototype._verifyProgress = function( progress ){
    if(this.isUploadComplete) return;
  	if(progress == null || this.progress == progress){
      this.xhr.abort();
      this.onError();
  	}else{
    	this.progress = progress;
    	this._startVerifyProgress( null );
  	}
  }
  
  /* This class will make a uploader using form and a hidden iframe */
  var IframeUploader = function(input, form, urlPost, urlProgress){
    this.inputFile = input;
    this.form = form;
    this.urlpost = urlPost;
    this.urlprogress = urlProgress;
  }
  IframeUploader.prototype = new BaseUploader();
  IframeUploader.prototype.start = function(){
    this.key = Util.getKey();
    var iframeId = "__upload_iframe__";
    var iframe = Util.create("iframe", {
     "id": iframeId,
     "name": iframeId,
     "width":"0", "height":"0", "border":"0",
     "style":"width: 0; height: 0; border: none;"
    });
   
    Util.addEvent(iframe, "load", this._uploadComplete, this);
    this.iframe = iframe;
    this.form.parentNode.appendChild(iframe);
    win.frames[iframeId].name = iframeId;
    this.form.setAttribute("target", iframeId);
    this.form.setAttribute("action", this.urlPost);
    this.form.submit();
    this.isUploadComplete = false;
    this.onStart();
    this.onProgress(0, -1, 0);
    var self = this;
    this.timeInterval = setTimeout(function(){
      self._uploadProgress();
    }, 800);
  }
  IframeUploader.prototype.setProgress = function(loaded, total){
    var progressTemp  = {lengthComputable:true, loaded:loaded, total:total};
    this._uploadProgress(progressTemp);
  }
  IframeUploader.prototype._getContentIFrame = function(iframe){
    var content = "";
    try{
      if (iframe.contentDocument) {
          content = iframe.contentDocument.body.innerHTML;
      } else if (iframe.contentWindow) {
          content = iframe.contentWindow.document.body.innerHTML;
      } else if (iframe.document) {
          content = iframe.document.body.innerHTML;
      }
    }catch(e){}
    return content;
  }
  IframeUploader.prototype._uploadComplete = function(){
    var iframe = Util.$("__upload_iframe__");
    var content = this._getContentIFrame(iframe);
    this.isUploadComplete = true;
    this.onComplete(content);
    clearTimeout(this.timeInterval);
    setTimeout(function(){
      try{
        Util.remove(iframe);
      }catch(e){}
    }, 250);
  }
  IframeUploader.prototype._uploadProgress = function(){
    var urlProgress = this.progressUrl + "&rand="+new Date().getTime();
    Util.XHR(urlProgress, "GET", Util.delegate(this,this._onCompleteXHRPoolingProgress));
  }
  IframeUploader.prototype._onCompleteXHRPoolingProgress = function(data){
    if(!this.isUploadComplete){
      var self = this;
      this.timeInterval = setTimeout(function(){
        self._uploadProgressByIframe();
      }, 800);
    }
    if(data === "{}") return;
    var json = eval('(' + data + ')');
    if(json.bytes_loaded){
      var percent = Math.round(json.bytes_loaded / json.bytes_total * 100);
      this.onProgress(json.bytes_loaded, json.bytes_total, percent);
    }
  }
  
  IframeUploader.prototype._onErrorXHR = function(data){
    //Retry
  }
  
  IframeUploader.prototype._startVerifyProgress = function( progress ){
  	clearTimeout(this.checkProgresstimeInterval);
  	var self = this;
    this.checkProgresstimeInterval = setTimeout(function(){
          self._verifyProgress( progress );
    }, 10000);
  }
  IframeUploader.prototype._verifyProgress = function( progress ){
    if(this.isUploadComplete) return;
  	if(progress == null || this.progress == progress){
      Util.remove(Util.$("__upload_iframe__"));
      this.onError();
  	}else{
    	this.progress = progress;
    	this._startVerifyProgress( null );
  	}
  }
  
  var Uploader = function(form, inputFile, progressUrl, uploadUrl){
    this.form = typeof(form) === "string" ? Util.$(form) : form;
    this.input = typeof(inputFile) === "string" ? Util.$(inputFile) : inputFile;
    this.progressUrl = progressUrl;
    this.uploadUrl = uploadUrl;
    this.xhrSupport = Util.hasXHRUpload();
    this.init();
  }
  Uploader.prototype = {
    /* These functions show be replace by callbacks for each action */
    onProgress:function(){},
    onComplete:function(){},
    onCancel:function(){},
    onError:function(){},
    onStart:function(){},
    /* These functions show be replace by callbacks for each actions */
    init:function(){
      this.form.setAttribute("enctype","multipart/form-data");
      this.form.setAttribute("encoding", "multipart/form-data");
      this.form.setAttribute("method" , "post");
      this.upload = this._getUploaderInstance();
      Util.addEvent(this.input, "change", this._onChangeInput, this);
    },
    start:function(){
      this.key = Util.getKey();
      this._registerEvents();
      this.upload.progressUrl = this.progressUrl + "?uploadKey=" + this.key;
      this.upload.urlPost = this.uploadUrl + "?uploadKey=" + this.key;
      this.upload.start();      
    },
    isUploadComplete:function(){
      return this.upload.isUploadComplete||false;
    },
    setProgress:function(loaded, total){
    	this.upload.setProgress(loaded, total);
    },
    _getUploaderInstance:function(){
      var uploaderMethod = {
        true:XHRUploader,
        false:IframeUploader
      };
      var instance = new uploaderMethod[this.xhrSupport](this.input, this.form, this.urlPost, this.progressUrl);
      return instance;
    },
    _registerEvents:function(){
      var self = this;
      this.upload.onProgress = function(bytes_loaded, bytes_total, perc){ 
          self.onProgress(bytes_loaded, bytes_total, perc);
      }
      this.upload.onComplete = function(arg){ self.onComplete(arg); }
      this.upload.onError = function(){ self.onError(); }
      this.upload.onStart = function(){ self.onStart(); }
    },
    _onChangeInput:function(){
      this.start();
    }
  }
  var _superUpload = function(form, inputFile, description, saveButton, 
                              progressUrl, uploadUrl, saveUrl, timeForUpdate ){
    this.form = Util.$(form);
    this.inputFile = Util.$(inputFile);
    this.description = Util.$(description);
    this.saveButton = Util.$(saveButton);
    this.progressUrl = progressUrl;
    this.uploadUrl = uploadUrl;
    this.saveUrl = saveUrl;
    this.timeForUpdate = timeForUpdate;
    this.init();
  }
  _superUpload.prototype = {
    init:function(){
      this.file = new Uploader(this.form, this.inputFile, this.progressUrl, this.uploadUrl, this.timeForUpdate);
      Util.addEvent(this.saveButton, "click", this._onClickSave, this);
    },
    _onClickSave:function(){
      var params = "uploadKey=" + this.file.key + "&description="+ this.description.value;
      Util.XHR(this.saveUrl, "POST", Util.delegate(this,this._onSaveComplete), params);
    },
    _onSaveComplete:function(data){
      win.location.href = this.saveUrl+"?uploadKey=" + this.file.key;
    }
  }
  win.Uploader = Uploader;
  win.SuperUpload = _superUpload;
}(document,window));