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

        console.log("token is", tokenId);

        // Ok so let's clone the preview
        pageHtml = $(".letter-preview .page").clone();
        // Then let's blank out the names since Lob will print those (I think)
        pageHtml.find("#return-address-text").text('');
        pageHtml.find("#recipient-address-text").text('');
        // Then let's remove the color that was showing the window's boundaries
        pageHtml.find("#return-address-window").css('background-color', 'transparent');
        pageHtml.find("#recipient-address-window").css('background-color', 'transparent');

        data['html'] = pageHtml.outerHTML();

        $.post("/send-letter", data, function(res) {
            if (res.success == true) {
                $('#after-send-attempt .modal-body p').text("Your letter is on its way!");
            }
            else {
                // modal text displays error
                var error = res.error;
                $('#after-send-attempt .modal-body p').text(error, "Please try again.");
            }
            $('#after-send-attempt').modal('show');
        });
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

// Give the modal an identity
$('#after-send-attempt').modal({"show": false});