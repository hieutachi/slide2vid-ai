# Read-only Windows Core Audio inspection. Does not change volume or output device.
$ErrorActionPreference = 'Stop'
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;

[ComImport, Guid("BCDE0395-E52F-467C-8E3D-C4579291692E")]
class MMDeviceEnumerator {}
[ComImport, Guid("A95664D2-9614-4F35-A746-DE8DB63617E6"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IDevices {
    int EnumAudioEndpoints(int flow, uint mask, out IntPtr devices);
    [PreserveSig] int GetDefaultAudioEndpoint(int flow, int role, out IDevice device);
    int GetDevice([MarshalAs(UnmanagedType.LPWStr)] string id, out IDevice device);
    int RegisterEndpointNotificationCallback(IntPtr client);
    int UnregisterEndpointNotificationCallback(IntPtr client);
}
[ComImport, Guid("D666063F-1587-4E43-81F1-B948E807363F"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IDevice {
    [PreserveSig] int Activate(ref Guid iid, uint context, IntPtr args, [MarshalAs(UnmanagedType.IUnknown)] out object result);
    int OpenPropertyStore(uint access, out IntPtr store);
    [PreserveSig] int GetId([MarshalAs(UnmanagedType.LPWStr)] out string id);
    int GetState(out uint state);
}
[ComImport, Guid("5CDF2C82-841E-4546-9722-0CF74078229A"), InterfaceType(ComInterfaceType.InterfaceIsIUnknown)]
interface IVolume {
    int RegisterControlChangeNotify(IntPtr notify);
    int UnregisterControlChangeNotify(IntPtr notify);
    int GetChannelCount(out uint channels);
    int SetMasterVolumeLevel(float db, ref Guid context);
    int SetMasterVolumeLevelScalar(float scalar, ref Guid context);
    int GetMasterVolumeLevel(out float db);
    [PreserveSig] int GetMasterVolumeLevelScalar(out float scalar);
    int SetChannelVolumeLevel(uint channel, float db, ref Guid context);
    int SetChannelVolumeLevelScalar(uint channel, float scalar, ref Guid context);
    int GetChannelVolumeLevel(uint channel, out float db);
    int GetChannelVolumeLevelScalar(uint channel, out float scalar);
    int SetMute([MarshalAs(UnmanagedType.Bool)] bool mute, ref Guid context);
    [PreserveSig] int GetMute([MarshalAs(UnmanagedType.Bool)] out bool mute);
}
public class OutputState {
    public int Role;
    public string Id;
    public float VolumePercent;
    public bool Muted;
    public static OutputState Read(int role) {
        var devices = (IDevices)new MMDeviceEnumerator();
        IDevice device;
        Marshal.ThrowExceptionForHR(devices.GetDefaultAudioEndpoint(0, role, out device));
        string id;
        Marshal.ThrowExceptionForHR(device.GetId(out id));
        Guid iid = new Guid("5CDF2C82-841E-4546-9722-0CF74078229A");
        object obj;
        Marshal.ThrowExceptionForHR(device.Activate(ref iid, 23, IntPtr.Zero, out obj));
        var volume = (IVolume)obj;
        float level;
        bool mute;
        Marshal.ThrowExceptionForHR(volume.GetMasterVolumeLevelScalar(out level));
        Marshal.ThrowExceptionForHR(volume.GetMute(out mute));
        Marshal.ReleaseComObject(obj);
        Marshal.ReleaseComObject(device);
        Marshal.ReleaseComObject(devices);
        return new OutputState {Role=role, Id=id, VolumePercent=level*100, Muted=mute};
    }
}
'@
$results = foreach ($role in 0, 1, 2) {
    $state = [OutputState]::Read($role)
    $endpoint = [regex]::Match($state.Id, '\{[0-9a-fA-F-]+\}$').Value
    $key = "HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render\$endpoint\Properties"
    $properties = Get-ItemProperty -LiteralPath $key -ErrorAction SilentlyContinue
    [pscustomobject]@{
        role = @('console', 'multimedia', 'communications')[$role]
        endpoint_id = $state.Id
        friendly_name = $properties.'{b3f8fa53-0004-438e-9003-51a46e139bfc},6'
        description = $properties.'{a45c254e-df1c-4efd-8020-67d146a850e0},2'
        volume_percent = [math]::Round($state.VolumePercent, 1)
        muted = $state.Muted
    }
}
$results | ConvertTo-Json -Depth 4