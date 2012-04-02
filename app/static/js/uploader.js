(function(doc, win){
  var _uploader = function(form, inputFile, progressUrl, timeForUpdate){ //change to use options args

    this.form = typeof(form) === "string" ? Util.$(form) : form;
    this.input = typeof(inputFile) === "string" ? Util.$(inputFile) : inputFile;
    this.progressUrl = progressUrl;
    this.timeForUpdate = timeForUpdate;
    this.xhrSupport = Util.hasXHRUpload();
    this.timeInterval;
    this.isUploadComplete = false;
    this.init();
  }
  _uploader.prototype = {
    onProgress:function(){},
    onComplete:function(){},
    onCancel:function(){},
    onError:function(){},
    onStart:function(){},
    init:function(){
      this.form.setAttribute("enctype","multipart/form-data");
      this.form.setAttribute("encoding", "multipart/form-data");
      this.form.setAttribute("method" , "post");
      Util.addEvent(this.input, "change", this._onChangeInput, this);
    },
    _onChangeInput:function(){
      if(this.xhrSupport){
        this.startUploadByXHR();
      }else{
        this.startUploadByIframe();
      }
    },
    startUploadByXHR:function(){
      this.key = Util.getKey();
      var fd = new FormData();
      var file = this.input.files[0];
      fd.append("fileToUpload", file);
      var xhr = new XMLHttpRequest();
      Util.addEvent(xhr.upload, "progress", this._uploadProgress, this);
      Util.addEvent(xhr, "load", this._uploadComplete, this);
      Util.addEvent(xhr, "error", this._uploadFailed, this);
      Util.addEvent(xhr, "abort", this._uploadCanceled, this);
      xhr.open("POST", this.form.action + "?uploadKey=" + this.key);
      xhr.setRequestHeader("X-FileName", file.name);
      xhr.setRequestHeader("FileType", file.type);
      xhr.setRequestHeader("Content-Type", file.type);
      xhr.setRequestHeader("Content-length", file.size);
      xhr.setRequestHeader("FileSize", file.size);
      xhr.send(fd);
      this.onStart();
    },
    _uploadComplete:function(evt){
      this.onComplete(evt.currentTarget.responseText);
    },
    _uploadFailed:function(evt){
      this.onError();
    },
    _uploadCanceled:function(evt){
      this.onCancel();        
    },
    _uploadProgress:function(evt){
      if (evt.lengthComputable) {
        var percent = Math.round(evt.loaded / evt.total * 100);
        this.onProgress(evt.loaded, evt.total, percent);
      }else {
        // vou ter que chamar a url /progress?
      }
    },
    _onCompleteXHRPooling:function(data){
        if(!this.isUploadComplete){
          var self = this;
          
          this.timeInterval = setTimeout(function(){
            self._uploadProgressByIframe();
          }, this.timeForUpdate);
        }
        if(data == "None") return;
        var json = eval('('+data+')');
        var percent = Math.round(json.bytes_loaded / json.bytes_total * 100);
        this.onProgress(json.bytes_loaded, json.bytes_total, percent);
    },
    _onErrorXHR:function(data){
      //Retry
    },
    _uploadProgressByIframe:function(){
      var params = "?uploadKey=" + this.key + "&rand="+new Date().getTime();
      Util.XHR(this.progressUrl, "GET", Util.delegate(this,this._onCompleteXHRPooling), params);
    },
    startUploadByIframe:function(){
      this.key = Util.getKey();
      var iframeId = this.key + "__upload_iframe__";
      var iframe = Util.create("iframe", {
       "id": iframeId,
       "name": iframeId,
       "width":"0", "height":"0", "border":"0",
       "style":"width: 0; height: 0; border: none;"
      });
     
      Util.addEvent(iframe, "load", this.onLoadIframe, this);
      this.iframe = iframe;
      this.form.parentNode.appendChild(iframe);
      win.frames[iframeId].name = iframeId;
      this.form.setAttribute("target", iframeId);
      this.form.setAttribute("action", "/uploader?uploadKey=" + this.key); //usar um hidden
    
      this.form.submit();
      this.onStart();
      this.onProgress(0, -1, 0);
      var self = this;
      this.timeInterval = setTimeout(function(){
        self._uploadProgressByIframe();
      }, this.timeForUpdate);
    },
    onLoadIframe:function(){
      var iframeId = this.key + "__upload_iframe__";
      var iframe = Util.$(iframeId);
      this.isUploadComplete = true;
      clearTimeout(this.timeInterval);
      //Util.removeEvent(this.iframe, "load");
      var content = "";
      if (iframe.contentDocument) {
          content = iframe.contentDocument.body.innerHTML;
      } else if (iframe.contentWindow) {
          content = iframe.contentWindow.document.body.innerHTML;
      } else if (iframe.document) {
          content = iframe.document.body.innerHTML;
      }
      this.onComplete(content);
      setTimeout(function(){
        Util.remove(Util.$(iframeId));
      }, 250);

    }
  }
  var _superUpload = function(form, inputFile, description, saveButton, 
                              progressUrl, saveUrl, timeForUpdate ){
    this.form = Util.$(form);
    this.inputFile = Util.$(inputFile);
    this.description = Util.$(description);
    this.saveButton = Util.$(saveButton);
    this.progressUrl = progressUrl;
    this.saveUrl = saveUrl;
    this.timeForUpdate = timeForUpdate;
    this.init();
  }
  _superUpload.prototype = {
    init:function(){
      this.file = new Uploader(this.form, this.inputFile, this.progressUrl, this.timeForUpdate);
      Util.addEvent(this.saveButton, "click", this._onClickSave, this);
    },
    _onClickSave:function(){
      var params = "uploadKey=" + this.key + "&description="+ this.description.value;
      Util.XHR(this.saveUrl, "POST", Util.delegate(this,this._onSaveComplete), params);
      
    },
    _onSaveComplete:function(data){
      alert(data);
    }
  }
  win.Uploader = _uploader;
  win.SuperUpload = _superUpload;
}(document,window));