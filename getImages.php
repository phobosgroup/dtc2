<?php

	$dir = ".";
	if(is_dir($dir)){
		if($dd = opendir($dir)){
			while (($f = readdir($dd)) !== false)
				#if(preg_match("/.jpg/", $f)) {
					#$files[] = $f;
				#}
				array_multisort(array_map('filemtime', ($files = glob("*.jpg"))), SORT_DESC, $files);
			closedir($dd);
		} 
	
	$response = "";
		foreach ($files as $img){
			echo $img.';';
		}
	}
?>
