Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Windows.Forms.DataVisualization
Add-Type @"
    using System;
    using System.Runtime.InteropServices;
    public class NativeMethods {
        [DllImport("dwmapi.dll", PreserveSig = false)]
        public static extern int DwmSetWindowAttribute(IntPtr hwnd, int attr, ref int attrValue, int attrSize);
        public static void dark(IntPtr Hwnd) //Hwnd is the handle to your window
        {
            int renderPolicy = 1;
            DwmSetWindowAttribute(Hwnd, 20, ref renderPolicy, sizeof(int));
        }        
    }
"@
$Black = [System.Drawing.Color]::Black
$White = [System.Drawing.Color]::White

function plot_vmaf($data){
    $chart = New-Object System.Windows.Forms.DataVisualization.Charting.Chart
    $chart_area = New-Object System.Windows.Forms.DataVisualization.Charting.ChartArea
    $legend = New-Object System.Windows.Forms.DataVisualization.Charting.Legend
    $chart.ChartAreas.Add($chart_area)
    $chart.Legends.Add($legend)
    $chart.Dock = [System.Windows.Forms.DockStyle]::Fill
    $chart_area.AxisY.IsStartedFromZero = $false;
    $chart_area.BackColor = $Black
    $chart_area.AxisX.LineColor = $chart_area.AxisX.MajorGrid.LineColor = $chart_area.AxisX.LabelStyle.ForeColor = $White
    $chart_area.AxisY.LineColor = $chart_area.AxisY.MajorGrid.LineColor = $chart_area.AxisY.LabelStyle.ForeColor = $White
    $chart.BackColor = $legend.BackColor = $Black
    $chart.ForeColor = $legend.ForeColor = $White

    $data.keys | sort | ForEach-Object {
        $chart.Series.Add($_) | out-null
        $chart.Series[$_].ChartType = [System.Windows.Forms.DataVisualization.Charting.SeriesChartType]::Line
        $chart.Series[$_].Points.DataBindXY($data[$_].Frame, $data[$_].vmaf)
        $chart.Series[$_].MarkerStyle = 2;
    }

    $window = New-Object System.Windows.Forms.Form
    [NativeMethods]::dark($window.Handle)
    $window.Controls.Add($chart)
    $window.Size = [System.Drawing.Size]::new(800,500)
    $window.ShowDialog()
}

#Read-Host -Prompt "Press any key to continue"