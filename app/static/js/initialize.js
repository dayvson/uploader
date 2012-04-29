window.onload = function(){
  var superUpload = new SuperUpload("uploader", "datafile", "description", 
                                    "savebutton", "/progress", "/uploader", "/save");
  superUpload.file.onProgress = function(bytes_loaded, bytes_total, perc){
      console.log(bytes_loaded, bytes_total, perc);
      Util.$("progressFill").style.width = perc + "%";
      Util.$("progressFill").innerHTML = perc+ "%";
  }
  superUpload.file.onStart = function(){
    this.input.disabled = true;
    Util.$("savebutton").disabled = true;
    Util.$("uploadLink").href="#";
    Util.$("uploadLink").innerHTML = "";
  }
  superUpload.file.onError = function(data){
    alert("Error, please retry!");
  }
  superUpload.file.onComplete = function(data){
      this.onProgress(1,1,100);
      Util.$("uploadLink").href=data;
      Util.$("uploadLink").innerHTML = "Uploaded to Here";
      Util.$("savebutton").disabled = false;
      this.input.disabled = false;
  }
}
