  $(document).ready(function(){
    $("#progress").animate({
       width: "0%"
    }, 15000, function() {
      //page_reload();
      }
    );

  });

  function page_reload()
  {
    $.ajax({
      type: "HEAD",
      url: window.location,
      success: function() {
        window.location.reload();
      },
      error: function() {
        console.log("error reloading page.");
        setTimeout(page_reload, 60000);
      },
      statusCode: {
        404: function() { console.log("404"); },
        501: function() { console.log("501"); },
        502: function() { console.log("502"); }
      }
    });
  }

  function getAndSetMaxCellHeight(tag) {
    let max = 0;
    const elements = document.querySelectorAll(tag);
    for (const el of elements){
        if (el.offsetHeight > max)
            max = el.offsetHeight
    }
    for (const el of elements){
        el.style.height = `${max}px`;
    }
  }

  function resizeRows() {
      for (const child of document.querySelector("grid-child").children) {
          getAndSetMaxCellHeight(child.tagName);
      }
  }

$(resizeRows)