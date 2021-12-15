<?php

// php -S 127.0.0.1:8080 index.php

########################
### API Intermediate ###
########################

// HEADERS
header("Access-Control-Allow-Origin: *"); // CORS
header("Access-Control-Allow-Headers: *"); // CORS
header("Access-Control-Allow-Methods: GET, POST, OPTIONS"); // CORS
header('Content-Type: application/json; charset=utf-8');

$TOKEN = "Bearer bbf9537bc4b6b0a40c6665967cb9f759620cd611";
$headers = getallheaders();
if ($headers["Authorization"] != $TOKEN) {
    echo json_encode(array('status' => FALSE, 'message' => 'El TOKEN es incorrecto'));
    exit();
}

$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = str_replace("/apisearch/index.php/", "", $path);
$path = str_replace("/", "", $path);

if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0) {
    $content = trim(file_get_contents('php://input'));
    $data_array = array();
    if (!empty($content)) {
        $data_array = json_decode($content, TRUE);
    }
}


################
### API JINA ###
################

$url = "http://10.128.0.17:8000/$path";
$ch = curl_init($url);

if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0) {
    $payload = json_encode($data_array);
    curl_setopt($ch, CURLOPT_POST, TRUE);
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
}

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

// format response
if ($path == 'docs') {
    header('Content-Type: text/html; charset=utf-8');
}

if (isset($data_array["parameters"]["origin"]) && $data_array["parameters"]["origin"] == 'chatbot') {
    if ($path == 'search') {
        $response = json_decode($response, TRUE);
        $docs = $response['data']['docs'][0];
        if (empty($docs['matches'])) {
            echo json_encode(array('status' => FALSE, 'message' => 'No hay coincidencias'));
        } else {
            //$docs['matches'][0]['tags']['answer'] = $docs['matches'][0]['tags']['answer'] . "\n\n¿Deseas realizar otra consulta?";
            echo json_encode($docs['matches'][0]['tags']);
        }
    } else {
        echo $response;
    }
} else {
    echo $response;
}
