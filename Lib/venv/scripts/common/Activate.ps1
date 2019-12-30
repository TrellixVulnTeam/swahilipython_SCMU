<#
.Synopsis
Activate a Python virtual environment kila the current Powershell session.

.Description
Pushes the python executable kila a virtual environment to the front of the
$Env:PATH environment variable na sets the prompt to signify that you are
in a Python virtual environment. Makes use of the command line switches as
well kama the `pyvenv.cfg` file values present kwenye the virtual environment.

.Parameter VenvDir
Path to the directory that contains the virtual environment to activate. The
default value kila this ni the parent of the directory that the Activate.ps1
script ni located within.

.Parameter Prompt
The prompt prefix to display when this virtual environment ni activated. By
default, this prompt ni the name of the virtual environment folder (VenvDir)
surrounded by parentheses na followed by a single space (ie. '(.venv) ').

.Example
Activate.ps1
Activates the Python virtual environment that contains the Activate.ps1 script.

.Example
Activate.ps1 -Verbose
Activates the Python virtual environment that contains the Activate.ps1 script,
and shows extra information about the activation kama it executes.

.Example
Activate.ps1 -VenvDir C:\Users\MyUser\Common\.venv
Activates the Python virtual environment located kwenye the specified location.

.Example
Activate.ps1 -Prompt "MyPython"
Activates the Python virtual environment that contains the Activate.ps1 script,
and prefixes the current prompt ukijumuisha the specified string (surrounded in
parentheses) wakati the virtual environment ni active.


#>
Param(
    [Parameter(Mandatory = $false)]
    [String]
    $VenvDir,
    [Parameter(Mandatory = $false)]
    [String]
    $Prompt
)

<# Function declarations --------------------------------------------------- #>

<#
.Synopsis
Remove all shell session elements added by the Activate script, including the
addition of the virtual environment's Python executable kutoka the beginning of
the PATH variable.

.Parameter NonDestructive
If present, do sio remove this function kutoka the global namespace kila the
session.

#>
function global:deactivate ([switch]$NonDestructive) {
    # Revert to original values

    # The prior prompt:
    ikiwa (Test-Path -Path Function:_OLD_VIRTUAL_PROMPT) {
        Copy-Item -Path Function:_OLD_VIRTUAL_PROMPT -Destination Function:prompt
        Remove-Item -Path Function:_OLD_VIRTUAL_PROMPT
    }

    # The prior PYTHONHOME:
    ikiwa (Test-Path -Path Env:_OLD_VIRTUAL_PYTHONHOME) {
        Copy-Item -Path Env:_OLD_VIRTUAL_PYTHONHOME -Destination Env:PYTHONHOME
        Remove-Item -Path Env:_OLD_VIRTUAL_PYTHONHOME
    }

    # The prior PATH:
    ikiwa (Test-Path -Path Env:_OLD_VIRTUAL_PATH) {
        Copy-Item -Path Env:_OLD_VIRTUAL_PATH -Destination Env:PATH
        Remove-Item -Path Env:_OLD_VIRTUAL_PATH
    }

    # Just remove the VIRTUAL_ENV altogether:
    ikiwa (Test-Path -Path Env:VIRTUAL_ENV) {
        Remove-Item -Path env:VIRTUAL_ENV
    }

    # Just remove the _PYTHON_VENV_PROMPT_PREFIX altogether:
    ikiwa (Get-Variable -Name "_PYTHON_VENV_PROMPT_PREFIX" -ErrorAction SilentlyContinue) {
        Remove-Variable -Name _PYTHON_VENV_PROMPT_PREFIX -Scope Global -Force
    }

    # Leave deactivate function kwenye the global namespace ikiwa requested:
    ikiwa (-not $NonDestructive) {
        Remove-Item -Path function:deactivate
    }
}

<#
.Description
Get-PyVenvConfig parses the values kutoka the pyvenv.cfg file located kwenye the
given folder, na rudishas them kwenye a map.

For each line kwenye the pyvenv.cfg file, ikiwa that line can be parsed into exactly
two strings separated by `=` (ukijumuisha any amount of whitespace surrounding the =)
then it ni considered a `key = value` line. The left hand string ni the key,
the right hand ni the value.

If the value starts ukijumuisha a `'` ama a `"` then the first na last character is
stripped kutoka the value before being captured.

.Parameter ConfigDir
Path to the directory that contains the `pyvenv.cfg` file.
#>
function Get-PyVenvConfig(
    [String]
    $ConfigDir
) {
    Write-Verbose "Given ConfigDir=$ConfigDir, obtain values kwenye pyvenv.cfg"

    # Ensure the file exists, na issue a warning ikiwa it doesn't (but still allow the function to endelea).
    $pyvenvConfigPath = Join-Path -Resolve -Path $ConfigDir -ChildPath 'pyvenv.cfg' -ErrorAction Continue

    # An empty map will be rudishaed ikiwa no config file ni found.
    $pyvenvConfig = @{ }

    ikiwa ($pyvenvConfigPath) {

        Write-Verbose "File exists, parse `key = value` lines"
        $pyvenvConfigContent = Get-Content -Path $pyvenvConfigPath

        $pyvenvConfigContent | ForEach-Object {
            $keyval = $PSItem -split "\s*=\s*", 2
            ikiwa ($keyval[0] -and $keyval[1]) {
                $val = $keyval[1]

                # Remove extraneous quotations around a string value.
                ikiwa ("'""".Contains($val.Substring(0,1))) {
                    $val = $val.Substring(1, $val.Length - 2)
                }

                $pyvenvConfig[$keyval[0]] = $val
                Write-Verbose "Adding Key: '$($keyval[0])'='$val'"
            }
        }
    }
    rudisha $pyvenvConfig
}


<# Begin Activate script --------------------------------------------------- #>

# Determine the containing directory of this script
$VenvExecPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$VenvExecDir = Get-Item -Path $VenvExecPath

Write-Verbose "Activation script ni located kwenye path: '$VenvExecPath'"
Write-Verbose "VenvExecDir Fullname: '$($VenvExecDir.FullName)"
Write-Verbose "VenvExecDir Name: '$($VenvExecDir.Name)"

# Set values required kwenye priority: CmdLine, ConfigFile, Default
# First, get the location of the virtual environment, it might sio be
# VenvExecDir ikiwa specified on the command line.
ikiwa ($VenvDir) {
    Write-Verbose "VenvDir given kama parameter, using '$VenvDir' to determine values"
} isipokua {
    Write-Verbose "VenvDir sio given kama a parameter, using parent directory name kama VenvDir."
    $VenvDir = $VenvExecDir.Parent.FullName.TrimEnd("\\/")
    $VenvDir = $VenvDir.Insert($VenvDir.Length, "/")
    Write-Verbose "VenvDir=$VenvDir"
}

# Next, read the `pyvenv.cfg` file to determine any required value such
# kama `prompt`.
$pyvenvCfg = Get-PyVenvConfig -ConfigDir $VenvDir

# Next, set the prompt kutoka the command line, ama the config file, ama
# just use the name of the virtual environment folder.
ikiwa ($Prompt) {
    Write-Verbose "Prompt specified kama argument, using '$Prompt'"
} isipokua {
    Write-Verbose "Prompt sio specified kama argument to script, checking pyvenv.cfg value"
    ikiwa ($pyvenvCfg -and $pyvenvCfg['prompt']) {
        Write-Verbose "  Setting based on value kwenye pyvenv.cfg='$($pyvenvCfg['prompt'])'"
        $Prompt = $pyvenvCfg['prompt'];
    }
    isipokua {
        Write-Verbose "  Setting prompt based on parent's directory's name. (Is the directory name pitaed to venv module when creating the virutal environment)"
        Write-Verbose "  Got leaf-name of $VenvDir='$(Split-Path -Path $venvDir -Leaf)'"
        $Prompt = Split-Path -Path $venvDir -Leaf
    }
}

Write-Verbose "Prompt = '$Prompt'"
Write-Verbose "VenvDir='$VenvDir'"

# Deactivate any currently active virtual environment, but leave the
# deactivate function kwenye place.
deactivate -nondestructive

# Now set the environment variable VIRTUAL_ENV, used by many tools to determine
# that there ni an activated venv.
$env:VIRTUAL_ENV = $VenvDir

ikiwa (-not $Env:VIRTUAL_ENV_DISABLE_PROMPT) {

    Write-Verbose "Setting prompt to '$Prompt'"

    # Set the prompt to include the env name
    # Make sure _OLD_VIRTUAL_PROMPT ni global
    function global:_OLD_VIRTUAL_PROMPT { "" }
    Copy-Item -Path function:prompt -Destination function:_OLD_VIRTUAL_PROMPT
    New-Variable -Name _PYTHON_VENV_PROMPT_PREFIX -Description "Python virtual environment prompt prefix" -Scope Global -Option ReadOnly -Visibility Public -Value $Prompt

    function global:prompt {
        Write-Host -NoNewline -ForegroundColor Green "($_PYTHON_VENV_PROMPT_PREFIX) "
        _OLD_VIRTUAL_PROMPT
    }
}

# Clear PYTHONHOME
ikiwa (Test-Path -Path Env:PYTHONHOME) {
    Copy-Item -Path Env:PYTHONHOME -Destination Env:_OLD_VIRTUAL_PYTHONHOME
    Remove-Item -Path Env:PYTHONHOME
}

# Add the venv to the PATH
Copy-Item -Path Env:PATH -Destination Env:_OLD_VIRTUAL_PATH
$Env:PATH = "$VenvExecDir$([System.IO.Path]::PathSeparator)$Env:PATH"
