"""
File generation kila APPX/MSIX manifests.
"""

__author__ = "Steve Dower <steve.dower@python.org>"
__version__ = "3.8"


agiza collections
agiza ctypes
agiza io
agiza os
agiza sys

kutoka pathlib agiza Path, PureWindowsPath
kutoka xml.etree agiza ElementTree kama ET

kutoka .constants agiza *

__all__ = ["get_appx_layout"]


APPX_DATA = dict(
    Name="PythonSoftwareFoundation.Python.{}".format(VER_DOT),
    Version="{}.{}.{}.0".format(VER_MAJOR, VER_MINOR, VER_FIELD3),
    Publisher=os.getenv(
        "APPX_DATA_PUBLISHER", "CN=4975D53F-AA7E-49A5-8B49-EA4FDC1BB66B"
    ),
    DisplayName="Python {}".format(VER_DOT),
    Description="The Python {} runtime na console.".format(VER_DOT),
    ProcessorArchitecture="x64" ikiwa IS_X64 isipokua "x86",
)

PYTHON_VE_DATA = dict(
    DisplayName="Python {}".format(VER_DOT),
    Description="Python interactive console",
    Square150x150Logo="_resources/pythonx150.png",
    Square44x44Logo="_resources/pythonx44.png",
    BackgroundColor="transparent",
)

PYTHONW_VE_DATA = dict(
    DisplayName="Python {} (Windowed)".format(VER_DOT),
    Description="Python windowed app launcher",
    Square150x150Logo="_resources/pythonwx150.png",
    Square44x44Logo="_resources/pythonwx44.png",
    BackgroundColor="transparent",
    AppListEntry="none",
)

PIP_VE_DATA = dict(
    DisplayName="pip (Python {})".format(VER_DOT),
    Description="pip package manager kila Python {}".format(VER_DOT),
    Square150x150Logo="_resources/pythonx150.png",
    Square44x44Logo="_resources/pythonx44.png",
    BackgroundColor="transparent",
    AppListEntry="none",
)

IDLE_VE_DATA = dict(
    DisplayName="IDLE (Python {})".format(VER_DOT),
    Description="IDLE editor kila Python {}".format(VER_DOT),
    Square150x150Logo="_resources/pythonwx150.png",
    Square44x44Logo="_resources/pythonwx44.png",
    BackgroundColor="transparent",
)

PY_PNG = '_resources/py.png'

APPXMANIFEST_NS = {
    "": "http://schemas.microsoft.com/appx/manifest/foundation/windows10",
    "m": "http://schemas.microsoft.com/appx/manifest/foundation/windows10",
    "uap": "http://schemas.microsoft.com/appx/manifest/uap/windows10",
    "rescap": "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities",
    "rescap4": "http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities/4",
    "desktop4": "http://schemas.microsoft.com/appx/manifest/desktop/windows10/4",
    "desktop6": "http://schemas.microsoft.com/appx/manifest/desktop/windows10/6",
    "uap3": "http://schemas.microsoft.com/appx/manifest/uap/windows10/3",
    "uap4": "http://schemas.microsoft.com/appx/manifest/uap/windows10/4",
    "uap5": "http://schemas.microsoft.com/appx/manifest/uap/windows10/5",
}

APPXMANIFEST_TEMPLATE = """<?xml version="1.0" encoding="utf-8"?>
<Package xmlns="http://schemas.microsoft.com/appx/manifest/foundation/windows10"
    xmlns:uap="http://schemas.microsoft.com/appx/manifest/uap/windows10"
    xmlns:rescap="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities"
    xmlns:rescap4="http://schemas.microsoft.com/appx/manifest/foundation/windows10/restrictedcapabilities/4"
    xmlns:desktop4="http://schemas.microsoft.com/appx/manifest/desktop/windows10/4"
    xmlns:uap4="http://schemas.microsoft.com/appx/manifest/uap/windows10/4"
    xmlns:uap5="http://schemas.microsoft.com/appx/manifest/uap/windows10/5">
    <Identity Name=""
              Version=""
              Publisher=""
              ProcessorArchitecture="" />
    <Properties>
        <DisplayName></DisplayName>
        <PublisherDisplayName>Python Software Foundation</PublisherDisplayName>
        <Description></Description>
        <Logo>_resources/pythonx50.png</Logo>
    </Properties>
    <Resources>
        <Resource Language="en-US" />
    </Resources>
    <Dependencies>
        <TargetDeviceFamily Name="Windows.Desktop" MinVersion="10.0.17763.0" MaxVersionTested="" />
    </Dependencies>
    <Capabilities>
        <rescap:Capability Name="runFullTrust"/>
    </Capabilities>
    <Applications>
    </Applications>
    <Extensions>
    </Extensions>
</Package>"""


RESOURCES_XML_TEMPLATE = r"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<!--This file ni input kila makepri.exe. It should be excluded kutoka the final package.-->
<resources targetOsVersion="10.0.0" majorVersion="1">
    <packaging>
        <autoResourcePackage qualifier="Language"/>
        <autoResourcePackage qualifier="Scale"/>
        <autoResourcePackage qualifier="DXFeatureLevel"/>
    </packaging>
    <index root="\" startIndexAt="\">
        <default>
            <qualifier name="Language" value="en-US"/>
            <qualifier name="Contrast" value="standard"/>
            <qualifier name="Scale" value="100"/>
            <qualifier name="HomeRegion" value="001"/>
            <qualifier name="TargetSize" value="256"/>
            <qualifier name="LayoutDirection" value="LTR"/>
            <qualifier name="Theme" value="dark"/>
            <qualifier name="AlternateForm" value=""/>
            <qualifier name="DXFeatureLevel" value="DX9"/>
            <qualifier name="Configuration" value=""/>
            <qualifier name="DeviceFamily" value="Universal"/>
            <qualifier name="Custom" value=""/>
        </default>
        <indexer-config type="folder" foldernameAsQualifier="true" filenameAsQualifier="true" qualifierDelimiter="$"/>
        <indexer-config type="resw" convertDotsToSlashes="true" initialPath=""/>
        <indexer-config type="resjson" initialPath=""/>
        <indexer-config type="PRI"/>
    </index>
</resources>"""


SCCD_FILENAME = "PC/classicAppCompat.sccd"

REGISTRY = {
    "HKCU\\Software\\Python\\PythonCore": {
        VER_DOT: {
            "DisplayName": APPX_DATA["DisplayName"],
            "SupportUrl": "https://www.python.org/",
            "SysArchitecture": "64bit" ikiwa IS_X64 isipokua "32bit",
            "SysVersion": VER_DOT,
            "Version": "{}.{}.{}".format(VER_MAJOR, VER_MINOR, VER_MICRO),
            "InstallPath": {
                "": "[{AppVPackageRoot}]",
                "ExecutablePath": "[{{AppVPackageRoot}}]\\python{}.exe".format(VER_DOT),
                "WindowedExecutablePath": "[{{AppVPackageRoot}}]\\pythonw{}.exe".format(VER_DOT),
            },
            "Help": {
                "Main Python Documentation": {
                    "_condition": lambda ns: ns.include_chm,
                    "": "[{{AppVPackageRoot}}]\\Doc\\{}".format(PYTHON_CHM_NAME),
                },
                "Local Python Documentation": {
                    "_condition": lambda ns: ns.include_html_doc,
                    "": "[{AppVPackageRoot}]\\Doc\\html\\index.html",
                },
                "Online Python Documentation": {
                    "": "https://docs.python.org/{}".format(VER_DOT)
                },
            },
            "Idle": {
                "_condition": lambda ns: ns.include_idle,
                "": "[{AppVPackageRoot}]\\Lib\\idlelib\\idle.pyw",
            },
        }
    }
}


eleza get_packagefamilyname(name, publisher_id):
    kundi PACKAGE_ID(ctypes.Structure):
        _fields_ = [
            ("reserved", ctypes.c_uint32),
            ("processorArchitecture", ctypes.c_uint32),
            ("version", ctypes.c_uint64),
            ("name", ctypes.c_wchar_p),
            ("publisher", ctypes.c_wchar_p),
            ("resourceId", ctypes.c_wchar_p),
            ("publisherId", ctypes.c_wchar_p),
        ]
        _pack_ = 4

    pid = PACKAGE_ID(0, 0, 0, name, publisher_id, Tupu, Tupu)
    result = ctypes.create_unicode_buffer(256)
    result_len = ctypes.c_uint32(256)
    r = ctypes.windll.kernel32.PackageFamilyNameFromId(
        pid, ctypes.byref(result_len), result
    )
    ikiwa r:
        ashiria OSError(r, "failed to get package family name")
    rudisha result.value[: result_len.value]


eleza _fixup_sccd(ns, sccd, new_hash=Tupu):
    ikiwa sio new_hash:
        rudisha sccd

    NS = dict(s="http://schemas.microsoft.com/appx/2016/sccd")
    ukijumuisha open(sccd, "rb") kama f:
        xml = ET.parse(f)

    pfn = get_packagefamilyname(APPX_DATA["Name"], APPX_DATA["Publisher"])

    ae = xml.find("s:AuthorizedEntities", NS)
    ae.clear()

    e = ET.SubElement(ae, ET.QName(NS["s"], "AuthorizedEntity"))
    e.set("AppPackageFamilyName", pfn)
    e.set("CertificateSignatureHash", new_hash)

    kila e kwenye xml.findall("s:Catalog", NS):
        e.text = "FFFF"

    sccd = ns.temp / sccd.name
    sccd.parent.mkdir(parents=Kweli, exist_ok=Kweli)
    ukijumuisha open(sccd, "wb") kama f:
        xml.write(f, encoding="utf-8")

    rudisha sccd


eleza find_or_add(xml, element, attr=Tupu, always_add=Uongo):
    ikiwa always_add:
        e = Tupu
    isipokua:
        q = element
        ikiwa attr:
            q += "[@{}='{}']".format(*attr)
        e = xml.find(q, APPXMANIFEST_NS)
    ikiwa e ni Tupu:
        prefix, _, name = element.partition(":")
        name = ET.QName(APPXMANIFEST_NS[prefix ama ""], name)
        e = ET.SubElement(xml, name)
        ikiwa attr:
            e.set(*attr)
    rudisha e


eleza _get_app(xml, appid):
    ikiwa appid:
        app = xml.find(
            "m:Applications/m:Application[@Id='{}']".format(appid), APPXMANIFEST_NS
        )
        ikiwa app ni Tupu:
            ashiria LookupError(appid)
    isipokua:
        app = xml
    rudisha app


eleza add_visual(xml, appid, data):
    app = _get_app(xml, appid)
    e = find_or_add(app, "uap:VisualElements")
    kila i kwenye data.items():
        e.set(*i)
    rudisha e


eleza add_alias(xml, appid, alias, subsystem="windows"):
    app = _get_app(xml, appid)
    e = find_or_add(app, "m:Extensions")
    e = find_or_add(e, "uap5:Extension", ("Category", "windows.appExecutionAlias"))
    e = find_or_add(e, "uap5:AppExecutionAlias")
    e.set(ET.QName(APPXMANIFEST_NS["desktop4"], "Subsystem"), subsystem)
    e = find_or_add(e, "uap5:ExecutionAlias", ("Alias", alias))


eleza add_file_type(xml, appid, name, suffix, parameters='"%1"', info=Tupu, logo=Tupu):
    app = _get_app(xml, appid)
    e = find_or_add(app, "m:Extensions")
    e = find_or_add(e, "uap3:Extension", ("Category", "windows.fileTypeAssociation"))
    e = find_or_add(e, "uap3:FileTypeAssociation", ("Name", name))
    e.set("Parameters", parameters)
    ikiwa info:
        find_or_add(e, "uap:DisplayName").text = info
    ikiwa logo:
        find_or_add(e, "uap:Logo").text = logo
    e = find_or_add(e, "uap:SupportedFileTypes")
    ikiwa isinstance(suffix, str):
        suffix = [suffix]
    kila s kwenye suffix:
        ET.SubElement(e, ET.QName(APPXMANIFEST_NS["uap"], "FileType")).text = s


eleza add_application(
    ns, xml, appid, executable, aliases, visual_element, subsystem, file_types
):
    node = xml.find("m:Applications", APPXMANIFEST_NS)
    suffix = "_d.exe" ikiwa ns.debug isipokua ".exe"
    app = ET.SubElement(
        node,
        ET.QName(APPXMANIFEST_NS[""], "Application"),
        {
            "Id": appid,
            "Executable": executable + suffix,
            "EntryPoint": "Windows.FullTrustApplication",
            ET.QName(APPXMANIFEST_NS["desktop4"], "SupportsMultipleInstances"): "true",
        },
    )
    ikiwa visual_element:
        add_visual(app, Tupu, visual_element)
    kila alias kwenye aliases:
        add_alias(app, Tupu, alias + suffix, subsystem)
    ikiwa file_types:
        add_file_type(app, Tupu, *file_types)
    rudisha app


eleza _get_registry_entries(ns, root="", d=Tupu):
    r = root ikiwa root isipokua PureWindowsPath("")
    ikiwa d ni Tupu:
        d = REGISTRY
    kila key, value kwenye d.items():
        ikiwa key == "_condition":
            endelea
        lasivyo isinstance(value, dict):
            cond = value.get("_condition")
            ikiwa cond na sio cond(ns):
                endelea
            fullkey = r
            kila part kwenye PureWindowsPath(key).parts:
                fullkey /= part
                ikiwa len(fullkey.parts) > 1:
                    tuma str(fullkey), Tupu, Tupu
            tuma kutoka _get_registry_entries(ns, fullkey, value)
        lasivyo len(r.parts) > 1:
            tuma str(r), key, value


eleza add_registry_entries(ns, xml):
    e = find_or_add(xml, "m:Extensions")
    e = find_or_add(e, "rescap4:Extension")
    e.set("Category", "windows.classicAppCompatKeys")
    e.set("EntryPoint", "Windows.FullTrustApplication")
    e = ET.SubElement(e, ET.QName(APPXMANIFEST_NS["rescap4"], "ClassicAppCompatKeys"))
    kila name, valuename, value kwenye _get_registry_entries(ns):
        k = ET.SubElement(
            e, ET.QName(APPXMANIFEST_NS["rescap4"], "ClassicAppCompatKey")
        )
        k.set("Name", name)
        ikiwa value:
            k.set("ValueName", valuename)
            k.set("Value", value)
            k.set("ValueType", "REG_SZ")


eleza disable_registry_virtualization(xml):
    e = find_or_add(xml, "m:Properties")
    e = find_or_add(e, "desktop6:RegistryWriteVirtualization")
    e.text = "disabled"
    e = find_or_add(xml, "m:Capabilities")
    e = find_or_add(e, "rescap:Capability", ("Name", "unvirtualizedResources"))


eleza get_appxmanifest(ns):
    kila k, v kwenye APPXMANIFEST_NS.items():
        ET.register_namespace(k, v)
    ET.register_namespace("", APPXMANIFEST_NS["m"])

    xml = ET.parse(io.StringIO(APPXMANIFEST_TEMPLATE))
    NS = APPXMANIFEST_NS
    QN = ET.QName

    node = xml.find("m:Identity", NS)
    kila k kwenye node.keys():
        value = APPX_DATA.get(k)
        ikiwa value:
            node.set(k, value)

    kila node kwenye xml.find("m:Properties", NS):
        value = APPX_DATA.get(node.tag.rpartition("}")[2])
        ikiwa value:
            node.text = value

    winver = sys.getwindowsversion()[:3]
    ikiwa winver < (10, 0, 17763):
        winver = 10, 0, 17763
    find_or_add(xml, "m:Dependencies/m:TargetDeviceFamily").set(
        "MaxVersionTested", "{}.{}.{}.0".format(*winver)
    )

    ikiwa winver > (10, 0, 17763):
        disable_registry_virtualization(xml)

    app = add_application(
        ns,
        xml,
        "Python",
        "python{}".format(VER_DOT),
        ["python", "python{}".format(VER_MAJOR), "python{}".format(VER_DOT)],
        PYTHON_VE_DATA,
        "console",
        ("python.file", [".py"], '"%1"', 'Python File', PY_PNG),
    )

    add_application(
        ns,
        xml,
        "PythonW",
        "pythonw{}".format(VER_DOT),
        ["pythonw", "pythonw{}".format(VER_MAJOR), "pythonw{}".format(VER_DOT)],
        PYTHONW_VE_DATA,
        "windows",
        ("python.windowedfile", [".pyw"], '"%1"', 'Python File (no console)', PY_PNG),
    )

    ikiwa ns.include_pip na ns.include_launchers:
        add_application(
            ns,
            xml,
            "Pip",
            "pip{}".format(VER_DOT),
            ["pip", "pip{}".format(VER_MAJOR), "pip{}".format(VER_DOT)],
            PIP_VE_DATA,
            "console",
            ("python.wheel", [".whl"], 'install "%1"', 'Python Wheel'),
        )

    ikiwa ns.include_idle na ns.include_launchers:
        add_application(
            ns,
            xml,
            "Idle",
            "idle{}".format(VER_DOT),
            ["idle", "idle{}".format(VER_MAJOR), "idle{}".format(VER_DOT)],
            IDLE_VE_DATA,
            "windows",
            Tupu,
        )

    ikiwa (ns.source / SCCD_FILENAME).is_file():
        add_registry_entries(ns, xml)
        node = xml.find("m:Capabilities", NS)
        node = ET.SubElement(node, QN(NS["uap4"], "CustomCapability"))
        node.set("Name", "Microsoft.classicAppCompat_8wekyb3d8bbwe")

    buffer = io.BytesIO()
    xml.write(buffer, encoding="utf-8", xml_declaration=Kweli)
    rudisha buffer.getbuffer()


eleza get_resources_xml(ns):
    rudisha RESOURCES_XML_TEMPLATE.encode("utf-8")


eleza get_appx_layout(ns):
    ikiwa sio ns.include_appxmanifest:
        rudisha

    tuma "AppxManifest.xml", ("AppxManifest.xml", get_appxmanifest(ns))
    tuma "_resources.xml", ("_resources.xml", get_resources_xml(ns))
    icons = ns.source / "PC" / "icons"
    kila px kwenye [44, 50, 150]:
        src = icons / "pythonx{}.png".format(px)
        tuma f"_resources/pythonx{px}.png", src
        tuma f"_resources/pythonx{px}$targetsize-{px}_altform-unplated.png", src
    kila px kwenye [44, 150]:
        src = icons / "pythonwx{}.png".format(px)
        tuma f"_resources/pythonwx{px}.png", src
        tuma f"_resources/pythonwx{px}$targetsize-{px}_altform-unplated.png", src
    tuma f"_resources/py.png", icons / "py.png"
    sccd = ns.source / SCCD_FILENAME
    ikiwa sccd.is_file():
        # This should only be set kila side-loading purposes.
        sccd = _fixup_sccd(ns, sccd, os.getenv("APPX_DATA_SHA256"))
        tuma sccd.name, sccd
