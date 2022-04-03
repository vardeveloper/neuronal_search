<?php

// php -S 127.0.0.1:8080 index.php

########################
### API Intermediate ###
########################

// HEADERS
//header("Access-Control-Allow-Origin: *"); // CORS
header("Access-Control-Allow-Headers: *"); // CORS
header("Access-Control-Allow-Methods: GET, POST, PUT, OPTIONS"); // CORS
header('Content-Type: application/json; charset=utf-8');

// validate API KEY
// $API_KEY = "bbf9537bc4b6b0a40c6665967cb9f759620cd611";
// $headers = getallheaders();
// if (base64_decode($headers["API_KEY"]) != $API_KEY) {
//     echo json_encode(array('status' => FALSE, 'message' => 'El API_KEY es incorrecto'));
//     exit();
// }

// remove path 
$path = parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH);
$path = str_replace("/index.php/", "", $path);
//$path = str_replace("/", "", $path);

// get data of body
if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0 ||
    strcasecmp($_SERVER['REQUEST_METHOD'], 'PUT') == 0) {
    $content = trim(file_get_contents('php://input'));
    $data_array = array();
    if (!empty($content)) {
        $data_array = json_decode($content, TRUE);
    }
}


################
### API JINA ###
################

$url = "http://127.0.0.1:8000/$path";
$ch = curl_init();
curl_setopt($ch, CURLOPT_URL, $url);

$authorization = '';
$headers = getallheaders();
if (isset($headers["Authorization"])) {
    $authorization = 'Authorization: ' . $headers["Authorization"];
}

if (strcasecmp($_SERVER['REQUEST_METHOD'], 'GET') == 0) {
    $headers = getallheaders();
    if (isset($headers["Authorization"])){
        curl_setopt($ch, CURLOPT_HTTPHEADER, array($authorization, 'Content-Type: application/json'));
        curl_setopt($ch, CURLINFO_HEADER_OUT, true);
    }
}

if (strcasecmp($_SERVER['REQUEST_METHOD'], 'POST') == 0) {
    if ($path == 'login/access-token') {
        curl_setopt($ch, CURLOPT_POST, TRUE);
        curl_setopt($ch, CURLOPT_POSTFIELDS, array('username' => $_POST['username'], 'password' => $_POST['password']));
    } elseif ($path == 'load_data') {
        $POST = array(
            'customer_code' => $_POST['customer_code'],
            'file' => $_FILES['file'],
        );
        print_r($_POST);
        curl_setopt($ch, CURLOPT_POST, TRUE);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array($authorization, 'Content-Type: multipart/form-data'));
        curl_setopt($ch, CURLOPT_POSTFIELDS, $POST);
        //curl_setopt($ch, CURLOPT_UPLOAD, 1);
        //curl_setopt($ch, CURLOPT_TIMEOUT, 86400); // 1 Day Timeout
    } else {
        $payload = json_encode($data_array);
        curl_setopt($ch, CURLOPT_HTTPHEADER, array($authorization, 'Content-Type: application/json'));
        curl_setopt($ch, CURLOPT_POST, TRUE);
        curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
    }
}

if (strcasecmp($_SERVER['REQUEST_METHOD'], 'PUT') == 0) {
    $payload = json_encode($data_array);
    curl_setopt($ch, CURLOPT_HTTPHEADER, array($authorization, 'Content-Type: application/json', 'Content-Length: ' . strlen($payload)));
    curl_setopt($ch, CURLOPT_CUSTOMREQUEST, 'PUT');
    curl_setopt($ch, CURLOPT_POSTFIELDS, $payload);
}

curl_setopt($ch, CURLOPT_FOLLOWLOCATION, TRUE);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, TRUE);

// Send the request
$response = curl_exec($ch);

// Check for errors
if ($response === FALSE) {
    die(curl_error($ch));
}

// Show what was sent in the header
// if (!curl_errno($ch)) {
//     $info = curl_getinfo($ch);
//     print_r($info['request_header']);
// }

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
            // $docs['matches'][0]['tags']['answer'] = $docs['matches'][0]['tags']['answer'] . "\n\n¿Deseas realizar otra consulta?";
            echo json_encode($docs['matches'][0]['tags']);
        }
    } else {
        echo $response;
    }
} else {
    echo $response;
}
