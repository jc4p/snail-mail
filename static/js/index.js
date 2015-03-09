$(document).ready(function() {
    function Editor(input, preview) {
        this.update = function() {
            // first just generate the HTML
            preview.innerHTML = markdown.toHTML(input.value);

            // then add in syntax highlighting just to be safe
            $(preview).find("pre code").each(function(i, block) {
                hljs.highlightBlock(block);
            });
        };

        input.editor = this;
        this.update();
    }
    var editor = new Editor($("#message-text")[0], $("#message-contents")[0]);

    $("#message-text").on('input', function(e) {
        editor.update();
    });

    // We should also update the From/To fields when they change them.
    $(".from-container input").on('input', function(e) {
        updateFrom();
    });

    $(".recipient-container input").on('input', function(e) {
        updateTo();
    });

    function updateFrom() {
        name = valOrDefault($("#from-name"), "Your Name");
        address = valOrDefault($("#from-address"), "Your Address");
        city = valOrDefault($("#from-location"), "Your City And State");
        updateViaInput($("#return-address-text"), name, address, city);

        // And do the image too
        imagePath = valOrDefault($("#from-image"), "");
        if (imagePath) {
            $("#return-address-image img").prop("src", imagePath);
            $("#return-address-image").show();
        } else {
            $("#return-address-image").hide();
        }
    }

    function updateTo() {
        name = valOrDefault($("#to-name"), "Their Name");
        address = valOrDefault($("#to-address"), "Their Address");
        city = valOrDefault($("#to-location"), "Their City And State");
        updateViaInput($("#recipient-address-text"), name, address, city);
    }

    function updateViaInput(textContainer, name, address, city) {
        textContainer.text(name)
        textContainer.append("<br>");
        textContainer.append(document.createTextNode(address));
        textContainer.append("<br>");
        textContainer.append(document.createTextNode(city));
    }

    function valOrDefault(elem, def) {
        return elem.val() ? elem.val() : def;
    }

    function sendLetter(tokenId) {
        data = $("#main-form").serializeObject();
        data['token'] = tokenId;

        // // Now make it so the window markers don't actually show on the real paper
        // pageHtml.find("#return-address-window").css("background-color", "transparent");
        // pageHtml.find("#recipient-address-window").css("background-color", "transparent");

        // html += pageHtml.outerHTML();
        // console.log($(html));

        // element = document.createElement("");
        // $(html).each(function(i, block) {
        //     element.innerHTML += block
        // });

        // Let's make a shadow clone first
        $(".shadow-div").html($(".letter-preview").clone())

        // Now let's remove the actual "we shouldn't be printing" stuff
        $(".shadow-div .letter-preview").addClass("letter-preview-print");
        $(".shadow-div .letter-preview").find("#return-address-text").text('');
        $(".shadow-div .letter-preview").find("#recipient-address-text").text('');

        // Now make it so the window markers don't actually show on the real paper
        $(".shadow-div .letter-preview").find("#return-address-window").css("background-color", "transparent");
        $(".shadow-div .letter-preview").find("#recipient-address-window").css("background-color", "transparent");

        var offScreenElement = $(".shadow-div")[0];
        actualHeight = $(".shadow-div").innerHeight();

        // Alright let's show the shadow DOM until we take a picture
        offScreenElement.style.position = 'relative';
        offScreenElement.style.left = window.innerWidth + 'px';
        offScreenElement.style.top = 0;

        html2canvas($(".shadow-div .letter-preview")[0], {
            logging: true,
            height: actualHeight,
            proxy: "html2canvas-proxy"})
            .then(function(canvas) {
                $(".shadow-div").attr('style', '')
                $(".shadow-div").text('');
                var dataUrl = canvas.toDataURL("image/png");
                var w = window.open();
                w.document.write('<img src="'+dataUrl+'"/>');
            });
        // $.post("/send-letter", data, function(res) {
        //     console.log(res);
        // });
    }

    $("#payment-btn-twitter").on('click', function(e) {
        sendLetter(1);
        e.preventDefault();
    });

    // Init stuff
    $("select").select2();
    $(".letter-preview").animate({scrollTop: $(".letter-preview")[0].scrollHeight});

    // Stripe stuff
    var handler = StripeCheckout.configure({
        key: 'pk_CTZI5qSX6WZy42tRUVkfOsYwfEQQo',
        token: function(token) {
            if (!token.hasOwnProperty('id')) {
                return;
            }

            sendLetter(token.id);
        }
    });

    $('#payment-btn-stripe').on('click', function(e) {
        // Open Checkout with further options
        handler.open({
            name: 'Send Letter',
            description: '1 Letter ($2.99)',
            amount: 299,
            bitcoin: true
        });
        e.preventDefault();
    });

    // Close Checkout on page navigation
    $(window).on('popstate', function() {
        handler.close();
    });
});


$.fn.serializeObject = function () {
   var o = {};
   var a = this.serializeArray();
   $.each(a, function () {
       if (o[this.name] !== undefined) {
           if (!o[this.name].push) {
               o[this.name] = [o[this.name]];
           }
           o[this.name].push(this.value || '');
       } else {
           o[this.name] = this.value || '';
       }
   });
   return o;
};

$.fn.outerHTML = function(s) {
  return (s)
  ? this.before(s).remove()
  : jQuery("<p>").append(this.eq(0).clone()).html();
}
