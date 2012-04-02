(function(doc, win){
  var util = {
    $:function(id){
      return document.getElementById(id);
    },
    addEvent:function(object, eventName, callback, scope){
      var func = scope ? this.delegate(scope, callback) : callback;
      if(object.addEventListener)
        object.addEventListener(eventName, func, true);
      else if(object.attachEvent)
        object.attachEvent('on'+eventName, func);
      return object;
    },
    delegate:function(obj, method){
      return function() { return method.apply(obj,arguments); };
    },
    removeEvent:function(object, eventName, callback){
      if(object.removeEventListener)
        object.removeEventListener(eventName, callback, false);
      else if(object.detachEvent)
        object.detachEvent('on'+eventName, callback);        
      return object;
    },
    create:function(type, attributes){
      var element = document.createElement(type);
      if(attributes){
        for(var attr in attributes){
          element.setAttribute(attr, attributes[attr]);
        }
      }
      return element;
    },
    remove:function(element){
      return element.parentNode.removeChild(element);
    }, 
    hasXHRUpload:function(){
      var xhrFileUpload = !!(win.XMLHttpRequestUpload && win.FileReader);
      var xhrFormData = !!win.FormData;
      return (xhrFileUpload && xhrFormData);

    },
    XHR:function(url, method, onComplete, _params, israw) {
      var params = _params||"";
      var xmlhttp;
      try {
          xmlhttp = new XMLHttpRequest();
      } catch(e) {
          var msxml = ['MSXML2.XMLHTTP.3.0', 'MSXML2.XMLHTTP', 'Microsoft.XMLHTTP'];
          for ( var i=0; i < msxml.length; i++ ) {
              try {
                  xmlhttp = new ActiveXObject(msxml[i]); break;
              } catch(e) {}
          }
      };
      xmlhttp.onreadystatechange = function() {
          if(this.readyState == 4  && this.status == 200) {
            onComplete(israw ? xmlhttp : this.responseText);
          }
      };
      xmlhttp.open(method, method == "GET" ? url+params : url);
      xmlhttp.setRequestHeader("Content-type","application/x-www-form-urlencoded");
      xmlhttp.setRequestHeader("Content-length", params.length);
      xmlhttp.setRequestHeader("Connection", "close");
      xmlhttp.send(params);
    },
    
    getKey:function(){
      var key = "";
      for (i = 0; i < 32; i++) { 
        key += Math.floor(Math.random() * 16).toString(16); 
      }
      return key;
    }
  };
  win.Util = util;
}(document,window));