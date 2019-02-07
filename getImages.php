<?php

	$dir = "uploads";
	if(is_dir($dir)){
		if($dd = opendir($dir)){
			while (($f = readdir($dd)) !== false)
				array_multisort(array_map('filemtime', ($files = glob("uploads/*.png"))), SORT_DESC, $files);
			closedir($dd);
		} 
	
	$response = "";
		foreach ($files as $img){
			echo $img.';';
		}
	}
?>

