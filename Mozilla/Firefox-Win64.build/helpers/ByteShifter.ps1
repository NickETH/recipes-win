

if ($args.Length -ne 3){
    echo "Aufruf: ByteShifter.ps1 Eingabedatei Ausgabedatei (-/[+])Offset"
}
else {
    $InputFile = $args[0]
    $OutputFile = $args[1]
    $Offset = $args[2]
    $bytes = [System.IO.File]::ReadAllBytes($InputFile)
    $bytesshiftet = $bytes
    [int]$singlebyte = 0
    [int]$newbyte = 0
    for ($i=0; $i -le ($bytes.length - 1); $i++) {
        $singlebyte = [int]$bytes[$i]
        # $singlebyte
        $newbyte = $singlebyte + $Offset
        # $newbyte
        $bytesshiftet[$i] = $newbyte
    }
    $CFGFile = [System.IO.File]::WriteAllBytes($OutputFile, $bytesshiftet)

}

# param([string]$inFile=$(Throw "Parameter missing: -inFile Path\File.ext"), [string]$outFile=$(Throw "Parameter missing: -outFile Path\File.ext")
#    [int]$Offset=$(Throw "Parameter missing: -Offset (+/-)number")
#    )
