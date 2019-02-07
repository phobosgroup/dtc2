<?php
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html><head><meta http-equiv="Content-Type" content="text/html; charset=windows-1256" /></head><body>

<form enctype="multipart/form-data" action="<?php echo $_SERVER['PHP_SELF']; ?>" method="POST">
Please choose a file: <input name="file" type="file" /><br />
<input type="submit" value="Upload" /></form>


<?php 

if (!empty($_FILES["file"]))
{
    if ($_FILES["file"]["error"] > 0)
       {echo "Error: " . $_FILES["file"]["error"] . "<br>";}
    else
       {echo "Stored file:".$_FILES["file"]["name"]."<br/>Size:".($_FILES["file"]["size"]/1024)." kB<br/>";
       move_uploaded_file($_FILES["file"]["tmp_name"],"uploads/".$_FILES["file"]["name"]);
       }
}
?>
