describe("Util", function() {
  function getBody(){
    return document.getElementsByTagName("body")[0];
  }
  
  it("should be able to find a element in DOM by ID", function() {
    expect(Util.$("test_id").id).toEqual("test_id");
    expect(Util.$("test_id")).toEqual(document.getElementById("test_id"));
  });

  it("should be able to create a element in DOM with arguments", function() {
    var element = Util.create("span", {"id":"new_span", "innerHTML":"test_create_element"});
    getBody().appendChild(element);
    expect(element.id).toEqual("new_span");
    expect(element).toEqual(Util.$("new_span"));
  });
  
  it("should be able to remove a DOM element", function() {
    var element = Util.create("span", {"id":"to_remove_test", "innerHTML":"to_remove_test"});
    getBody().appendChild(element);
    expect(element).toEqual(Util.$("to_remove_test"));
    Util.remove(element);
    expect(Util.$("to_remove_test")).toEqual(null);
  });
  
  it("should be able to return a key with 32bytes", function() {
    var key = Util.getKey();
    expect(key.length).toEqual(32);
  });
  
});