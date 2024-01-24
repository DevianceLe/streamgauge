<?php
//This pulls the info from weather.gov


//Defining My Variables
$fname = $_GET{"slapi"};
$fname = $fname . ".xml";
$fname2 = $_GET{"slapi"};
$dir = './tmp'; //Pretty much for storing stuffs
$fname3 = $dir . '/' . $fname;
$output = '"'; // We need quotes yo?
$output2 = ",";

//What will the file name be?
//echo "Debug 1 " . $fname . "<br>";
//echo "Debug 2 " . $fname2 . "<br>";
//echo "Debug 3 " . $dir . "<br>";
//echo "So uh what's the dir?" . $fname3 . "<br>";


//Ok let's pull the file CURL!
//Tempmenot?
$feedmedata = fopen($fname3, "w");
//Set the strings
$curlops = array(
    CURLOPT_FILE => $feedmedata,  //Obvs use for dynamic variables
    CURLOPT_TIMEOUT => 30,      // FFS it's just an xml
    CURLOPT_URL => "https://water.weather.gov/ahps2/hydrograph_to_xml.php?gage=" . $fname2 . "&output=xml",
    CURLOPT_HEADER => 0,
);

//Time to Execute
$ch = curl_init();
curl_setopt_array($ch, $curlops);
curl_exec($ch);
curl_close($ch);
fclose($feedmedata);

/// Now to produce the results
//Load up the file we saved?
$xmlDoc = simplexml_load_file($fname3);

//Define the fields
echo '"Time","Stage FT"';
echo "<br>";

$feedmedata = fopen($fname2 . '.csv', "w" , 1);
//echo $fname2;

fwrite($feedmedata, '"Time","Stage (ft)"' . PHP_EOL);
fclose($feedmedata);
$feedmedata = 0;



//Open it up
//This will be defined as something else later......
$i = 15; //Pulling only 15 records
while ($i > -1) {
    $feedmedata = fopen($fname2 . '.csv', "a");
    $outside = $xmlDoc->observed[0]->datum[$i]->valid;
    $cash = $xmlDoc->observed[0]->datum[$i]->primary;
    
	// This likes to go null at times. We make it always avail for google >_<
	$money = 0 + $xmlDoc->observed[0]->datum[$i]->secondary; 
	if ( 0 > $money ) {
		$money = 0; //Fixes it
	}
	$conversion = strtotime($outside) - 60*60*6; // <--- Need proper way for DST
    $conversion2 = date("h:i" , $conversion);
    $outside = $conversion2;
    
    echo $output . $outside . $output . $output2 . $output . $cash . $output;
    echo "<br>";
    
    fwrite($feedmedata, $output . $outside . $output . $output2 . $output . $cash . $output . PHP_EOL);
    $i--;
    fclose($feedmedata);
}
?>
