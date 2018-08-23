function importbatch()
{
    $('#IMPORT_WL').text("loading");
    var fdata = new FormData();
    fdata.append('opt', 'whitelist');
    fdata.append('stype', $('#id_stype').val());
    fdata.append('file', $('#id_batchfile')[0].files[0]);
    $.ajax({
        url : '/crawlfile/',
        data : fdata,
        cache : false,
        contentType : false,
        processData : false,
        type : 'POST',
        success : function(rdata) {
            $('#IMPORT_WL').text("开始导入");
            alert("上传成功")
        }
    });
}