<?php

########################
### API Intermediate ###
########################

$path_only = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path_only = str_replace("/index.php/", "", $path_only);
$path_only = str_replace("/", "", $path_only);
//echo $path_only;
//echo gettype($path_only);
//echo PHP_EOL;


// Make sure that it is a POST request.
if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') != 0) {
    throw new Exception('Request method must be POST!');
}

// Make sure that the content type of the POST request has been set to application/json
// $contentType = isset($_SERVER["CONTENT_TYPE"]) ? trim($_SERVER["CONTENT_TYPE"]) : '';
// if (strcasecmp($contentType, 'application/json') != 0) {
//     throw new Exception('Content type must be: application/json');
// }

// Receive the RAW post data.
$content = trim(file_get_contents('php://input'));

// Attempt to decode the incoming RAW post data from JSON.
$decoded = json_decode($content, true);

// If json_decode failed, the JSON is invalid.
if (!is_array($decoded)) {
    throw new Exception('Received content contained invalid JSON!');
}


################
### API JINA ###
################

$url = "http://10.128.0.17:8000/$path_only";
$ch = curl_init($url);
// Setup request to send json via POST.
$payload = json_encode($decoded);
// $payload = json_encode( 
//     array(
//         "data" => ["Es confiable guardar mi tarjeta"],
//         "parameters" => [
//             "business" => "ELCOMERCIO",
//             "category" => "Marketing"
//         ]
//     )
//  );

curl_setopt($ch, CURLOPT_POST, TRUE);
curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
curl_setopt($ch, CURLOPT_HTTPHEADER, array('Content-Type:application/json'));
curl_setopt($ch, CURLOPT_FOLLOWLOCATION, TRUE);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

// Send the request
$response = curl_exec($ch);

// Check for errors
if ($response === FALSE) {
    die(curl_error($ch));
}

// close curl
curl_close($ch);

// Response
// header("Access-Control-Allow-Origin: *");
// header("Access-Control-Allow-Headers: *");
// header("Access-Control-Allow-Methods: GET, POST, OPTIONS"); 
header('Content-Type: application/json; charset=utf-8');

if ($path_only == 'search') {
    $response = json_decode($response, true);
    $docs = $response['data']['docs'][0];
    if (empty($docs['matches'])) {
        echo json_encode(array('status' => false, 'message' => 'No hay coincidencias'));
    } else {
        echo json_encode($docs['matches'][0]['tags']);
    }
} else {
    echo $response;
}
