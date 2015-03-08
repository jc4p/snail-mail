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
    var editor = new Editor($("#message-text")[0], $("#letter-preview")[0]);

    $("#message-text").on('input', function(e) {
        editor.update();
    });
});