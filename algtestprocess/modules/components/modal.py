from dominate import tags


def modal():
    """Component which creates image preview"""
    with tags.div(
        className="modal fade flex flex-column justify-content-center align-items-center",
        id="imagemodal",
        tabindex="-1",
        aria_labelledby="myModalLabel",
        aria_hidden="true",
    ):
        with tags.div(className="modal-dialog", style="max-width: 75%;"):
            with tags.div(className="modal-content"):
                with tags.div(className="modal-body"):
                    tags.img(src="", className="imagepreview", style="width: 100%;")


def modal_script():
    """Script which opens preview of image"""
    tags.script(
        """
        $(function() {
        $('.pop').on('click', function() {
        $('.imagepreview').attr('src', $(this).find('img').attr('src'));
        $('#imagemodal').modal('show');   
        });		
        });
        """
    )
