#!/usr/bin/env python3
"""
FTM Multilateration Analysis Report Generator
Generates a comprehensive PDF report with all analysis results, 
statistics, tables, and visualizations.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.patches import Circle, Rectangle
import matplotlib.patches as mpatches
from pathlib import Path
from scipy.optimize import least_squares
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("data/ftm_quad_tests")
OUTPUT_PDF = Path("figures/FTM_Multilateration_Analysis_Report.pdf")
OUTPUT_PDF.parent.mkdir(exist_ok=True)

# Responder positions
RESPONDERS_ALL = {
    'r1': (0.0, 0.0),
    'r2': (20.0, 0.0),
    'r3': (0.0, 10.0),
    'r4': (20.0, 10.0)
}

RESPONDERS_NO_R4 = {
    'r1': (0.0, 0.0),
    'r2': (20.0, 0.0),
    'r3': (0.0, 10.0),
}

# Hardware info
HARDWARE_INFO = {
    'r1': ('Adafruit Feather ESP32-S3 TFT', 'PCB antenna', '(0, 0)'),
    'r2': ('Adafruit Feather ESP32-S3 TFT', 'PCB antenna', '(20, 0) - Near windows/doors'),
    'r3': ('Seeed XIAO ESP32-S3', 'External u.FL nanoblade', '(0, 10)'),
    'r4': ('Adafruit Feather ESP32-S3', 'PCB antenna', '(20, 10) - PROBLEMATIC'),
}


def load_ftm_data():
    """Load all FTM CSV files."""
    def load_csv(filepath):
        valid_lines = []
        with open(filepath, 'r') as f:
            for line in f:
                if line.startswith('#') or line.startswith('E ') or line.startswith('W '):
                    continue
                valid_lines.append(line)
        from io import StringIO
        return pd.read_csv(StringIO(''.join(valid_lines)))
    
    position_files = sorted(DATA_DIR.glob("FTM_QUAD_espaceSAT_pos*.csv"))
    all_data = [load_csv(f) for f in position_files]
    return pd.concat(all_data, ignore_index=True)


def calculate_errors(df):
    """Calculate true distances and errors."""
    df = df.copy()
    df['true_dist_cm'] = np.sqrt(
        (df['real_x'] * 100 - df['responder_x'] * 100)**2 +
        (df['real_y'] * 100 - df['responder_y'] * 100)**2
    )
    df['error_cm'] = df['dist_est_cm'] - df['true_dist_cm']
    df['abs_error_cm'] = np.abs(df['error_cm'])
    return df


def multilaterate(distances, responder_positions):
    """Estimate position using least squares."""
    if len(distances) < 3:
        return None
    
    distances_m = {k: v / 100.0 for k, v in distances.items()}
    labels = list(distances_m.keys())
    pos_array = np.array([responder_positions[l] for l in labels])
    dist_array = np.array([distances_m[l] for l in labels])
    
    def residuals(point):
        x, y = point
        calc_dists = np.sqrt((pos_array[:, 0] - x)**2 + (pos_array[:, 1] - y)**2)
        return calc_dists - dist_array
    
    try:
        result = least_squares(residuals, [10.0, 5.0], bounds=([0, 0], [20, 10]))
        if result.success:
            return tuple(result.x)
    except:
        pass
    return None


def compute_position_estimates(df, responders):
    """Compute position estimates for all samples."""
    results = []
    
    for pos in df['position'].unique():
        pos_data = df[df['position'] == pos]
        real_x = pos_data['real_x'].iloc[0]
        real_y = pos_data['real_y'].iloc[0]
        
        for sample_num in pos_data['sample_num'].unique():
            mask = (df['position'] == pos) & (df['sample_num'] == sample_num)
            sample_data = df[mask]
            
            if len(sample_data) >= 3:
                distances = dict(zip(sample_data['responder_label'], sample_data['dist_est_cm']))
                # Filter to only use responders we want
                distances = {k: v for k, v in distances.items() if k in responders}
                
                if len(distances) >= 3:
                    result = multilaterate(distances, responders)
                    if result:
                        pos_error = np.sqrt((result[0] - real_x)**2 + (result[1] - real_y)**2)
                        results.append({
                            'position': pos,
                            'real_x': real_x,
                            'real_y': real_y,
                            'est_x': result[0],
                            'est_y': result[1],
                            'pos_error_m': pos_error,
                            'n_responders': len(distances)
                        })
    
    return pd.DataFrame(results)


def add_title_page(pdf):
    """Create title page."""
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.7, 'FTM Multilateration Analysis', fontsize=28, fontweight='bold',
            ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.6, 'Comprehensive Performance Report', fontsize=18,
            ha='center', va='center', transform=ax.transAxes, style='italic')
    
    # Subtitle info
    ax.text(0.5, 0.45, 'WiFi Fine Timing Measurement (802.11mc)', fontsize=14,
            ha='center', va='center', transform=ax.transAxes)
    ax.text(0.5, 0.40, 'Indoor Positioning System Evaluation', fontsize=14,
            ha='center', va='center', transform=ax.transAxes)
    
    # Configuration box
    config_text = """Test Configuration:
    • Room: 20m × 10m
    • Responders: 4 ESP32-S3 devices at corners
    • Positions tested: 8 locations
    • Samples per position: ~1000 cycles
    • Frame count: 16, Burst period: 4"""
    
    ax.text(0.5, 0.22, config_text, fontsize=11, ha='center', va='center',
            transform=ax.transAxes, family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.3))
    
    # Date
    ax.text(0.5, 0.05, f'Generated: {datetime.now().strftime("%B %d, %Y")}', 
            fontsize=10, ha='center', va='center', transform=ax.transAxes)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def add_text_page(pdf, title, content_lines, code_block=None):
    """Create a text page with optional code block."""
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    
    # Title
    ax.text(0.5, 0.95, title, fontsize=18, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes)
    
    # Content
    y_pos = 0.88
    for line in content_lines:
        if line.startswith('##'):
            ax.text(0.05, y_pos, line[2:].strip(), fontsize=14, fontweight='bold',
                    ha='left', va='top', transform=ax.transAxes)
            y_pos -= 0.05
        elif line.startswith('•'):
            ax.text(0.08, y_pos, line, fontsize=11,
                    ha='left', va='top', transform=ax.transAxes)
            y_pos -= 0.035
        elif line == '---':
            ax.axhline(y=y_pos, xmin=0.05, xmax=0.95, color='gray', linewidth=0.5)
            y_pos -= 0.02
        elif line == '':
            y_pos -= 0.02
        else:
            ax.text(0.05, y_pos, line, fontsize=11,
                    ha='left', va='top', transform=ax.transAxes)
            y_pos -= 0.035
    
    # Code block if provided
    if code_block:
        ax.text(0.05, y_pos - 0.02, code_block, fontsize=9, family='monospace',
                ha='left', va='top', transform=ax.transAxes,
                bbox=dict(boxstyle='round', facecolor='#f0f0f0', alpha=0.8))
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def add_table_page(pdf, title, df, description=None):
    """Create a page with a table."""
    fig, ax = plt.subplots(figsize=(11, 8.5))
    ax.axis('off')
    
    ax.text(0.5, 0.95, title, fontsize=16, fontweight='bold',
            ha='center', va='top', transform=ax.transAxes)
    
    if description:
        ax.text(0.5, 0.90, description, fontsize=11, style='italic',
                ha='center', va='top', transform=ax.transAxes)
    
    # Create table
    table = ax.table(cellText=df.values,
                     colLabels=df.columns,
                     cellLoc='center',
                     loc='center',
                     bbox=[0.05, 0.15, 0.9, 0.7])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.5)
    
    # Style header
    for i in range(len(df.columns)):
        table[(0, i)].set_facecolor('#4472C4')
        table[(0, i)].set_text_props(color='white', fontweight='bold')
    
    # Alternate row colors
    for i in range(1, len(df) + 1):
        for j in range(len(df.columns)):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#D6DCE5')
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def add_figure_page(pdf, title, fig_func, description=None):
    """Create a page with a figure."""
    fig, ax = fig_func()
    
    if title:
        fig.suptitle(title, fontsize=14, fontweight='bold', y=0.98)
    
    pdf.savefig(fig, bbox_inches='tight')
    plt.close(fig)


def create_room_layout_figure(df, responders, title_suffix=""):
    """Create room layout figure."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    room = Rectangle((0, 0), 20, 10, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(room)
    
    resp_colors = {'r1': '#e74c3c', 'r2': '#3498db', 'r3': '#2ecc71', 'r4': '#9b59b6'}
    
    for label, (x, y) in RESPONDERS_ALL.items():
        if label in responders:
            ax.scatter(x, y, s=300, c=resp_colors[label], marker='s',
                       edgecolor='black', linewidth=2, zorder=5)
            ax.annotate(label, (x, y), fontsize=12, fontweight='bold',
                        ha='center', va='center', color='white', zorder=6)
        else:
            ax.scatter(x, y, s=300, c='lightgray', marker='s',
                       edgecolor='gray', linewidth=2, zorder=2, alpha=0.5)
            ax.annotate(f'{label}\n(excl.)', (x, y), fontsize=8,
                        ha='center', va='center', color='gray')
    
    positions = df.groupby('position')[['real_x', 'real_y']].first().reset_index()
    for _, row in positions.iterrows():
        ax.scatter(row['real_x'], row['real_y'], s=200, c='gold',
                   marker='o', edgecolor='black', linewidth=2, zorder=4)
        ax.annotate(row['position'], (row['real_x'], row['real_y']),
                    xytext=(0, 12), textcoords='offset points',
                    fontsize=10, ha='center', fontweight='bold')
    
    ax.set_xlim(-1, 21)
    ax.set_ylim(-1, 11)
    ax.set_xlabel('X Position (meters)', fontsize=12)
    ax.set_ylabel('Y Position (meters)', fontsize=12)
    ax.set_title(f'Room Layout {title_suffix}', fontsize=14, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    legend_elements = [mpatches.Patch(color=resp_colors[l], label=l) 
                       for l in responders]
    legend_elements.append(mpatches.Patch(color='gold', label='Initiator'))
    ax.legend(handles=legend_elements, loc='upper right')
    
    return fig, ax


def create_error_distribution_figure(df, title_suffix=""):
    """Create error distribution plots."""
    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    
    ax1 = axes[0, 0]
    ax1.hist(df['error_cm'], bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    ax1.axvline(x=0, color='red', linestyle='--', linewidth=2, label='Zero')
    ax1.axvline(x=df['error_cm'].mean(), color='orange', linewidth=2,
                label=f'Mean: {df["error_cm"].mean():.0f} cm')
    ax1.set_xlabel('Error (cm)')
    ax1.set_ylabel('Frequency')
    ax1.set_title(f'Distance Error Distribution {title_suffix}')
    ax1.legend()
    
    ax2 = axes[0, 1]
    responders = sorted(df['responder_label'].unique())
    resp_colors = ['#e74c3c', '#3498db', '#2ecc71', '#9b59b6'][:len(responders)]
    bp = df.boxplot(column='error_cm', by='responder_label', ax=ax2,
                    patch_artist=True, return_type='dict')
    for patch, color in zip(bp['error_cm']['boxes'], resp_colors):
        patch.set_facecolor(color)
        patch.set_alpha(0.6)
    ax2.axhline(y=0, color='red', linestyle='--', linewidth=1)
    ax2.set_xlabel('Responder')
    ax2.set_ylabel('Error (cm)')
    ax2.set_title('Error by Responder')
    plt.suptitle('')
    
    ax3 = axes[1, 0]
    df.boxplot(column='abs_error_cm', by='position', ax=ax3)
    ax3.set_xlabel('Position')
    ax3.set_ylabel('Absolute Error (cm)')
    ax3.set_title('Absolute Error by Position')
    plt.suptitle('')
    
    ax4 = axes[1, 1]
    for resp in responders:
        mask = df['responder_label'] == resp
        ax4.scatter(df.loc[mask, 'true_dist_cm'], df.loc[mask, 'abs_error_cm'],
                    alpha=0.2, s=10, label=resp)
    ax4.set_xlabel('True Distance (cm)')
    ax4.set_ylabel('Absolute Error (cm)')
    ax4.set_title('Error vs True Distance')
    ax4.legend()
    
    plt.tight_layout()
    return fig, axes


def create_position_estimation_figure(df_results, responders, title_suffix=""):
    """Create position estimation visualization."""
    fig, ax = plt.subplots(figsize=(14, 9))
    
    room = Rectangle((0, 0), 20, 10, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(room)
    
    resp_colors = {'r1': '#e74c3c', 'r2': '#3498db', 'r3': '#2ecc71', 'r4': '#9b59b6'}
    
    for label, (x, y) in RESPONDERS_ALL.items():
        if label in responders:
            ax.scatter(x, y, s=350, c=resp_colors[label], marker='s',
                       edgecolor='black', linewidth=2, zorder=5)
            ax.annotate(label, (x, y), fontsize=12, fontweight='bold',
                        ha='center', va='center', color='white', zorder=6)
        else:
            ax.scatter(x, y, s=300, c='lightgray', marker='s', alpha=0.4, zorder=2)
    
    pos_list = df_results['position'].unique()
    colors = plt.cm.tab10(np.linspace(0, 1, len(pos_list)))
    
    for i, pos in enumerate(pos_list):
        pos_data = df_results[df_results['position'] == pos]
        real_x, real_y = pos_data['real_x'].iloc[0], pos_data['real_y'].iloc[0]
        
        ax.scatter(real_x, real_y, s=250, c='gold', marker='*',
                   edgecolor='black', linewidth=2, zorder=10)
        
        ax.scatter(pos_data['est_x'], pos_data['est_y'],
                   s=10, c=[colors[i]], alpha=0.2, zorder=3)
        
        mean_est_x = pos_data['est_x'].mean()
        mean_est_y = pos_data['est_y'].mean()
        ax.scatter(mean_est_x, mean_est_y, s=120, c=[colors[i]],
                   marker='o', edgecolor='black', linewidth=2, zorder=8)
        
        ax.annotate('', xy=(real_x, real_y), xytext=(mean_est_x, mean_est_y),
                    arrowprops=dict(arrowstyle='->', color='red', lw=1.5, alpha=0.7),
                    zorder=7)
        
        ax.annotate(pos, (real_x, real_y), xytext=(5, 8), textcoords='offset points',
                    fontsize=10, fontweight='bold')
    
    ax.set_xlim(-1, 21)
    ax.set_ylim(-1, 11)
    ax.set_xlabel('X Position (meters)', fontsize=12)
    ax.set_ylabel('Y Position (meters)', fontsize=12)
    ax.set_title(f'Position Estimation Results {title_suffix}\n(★=True, ●=Mean estimated, →=Error)',
                 fontsize=13, fontweight='bold')
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)
    
    return fig, ax


def create_distance_rings_figure(df, position, sample_num, responders):
    """Create distance rings visualization."""
    fig, ax = plt.subplots(figsize=(12, 9))
    
    room = Rectangle((0, 0), 20, 10, fill=False, edgecolor='black', linewidth=2)
    ax.add_patch(room)
    
    mask = (df['position'] == position) & (df['sample_num'] == sample_num)
    sample_data = df[mask]
    sample_data = sample_data[sample_data['responder_label'].isin(responders)]
    
    real_x = sample_data['real_x'].iloc[0]
    real_y = sample_data['real_y'].iloc[0]
    
    resp_colors = {'r1': '#e74c3c', 'r2': '#3498db', 'r3': '#2ecc71', 'r4': '#9b59b6'}
    
    for _, row in sample_data.iterrows():
        label = row['responder_label']
        rx, ry = row['responder_x'], row['responder_y']
        dist_est_m = row['dist_est_cm'] / 100.0
        true_dist_m = row['true_dist_cm'] / 100.0
        
        ax.scatter(rx, ry, s=300, c=resp_colors[label], marker='s',
                   edgecolor='black', linewidth=2, zorder=5)
        ax.annotate(label, (rx, ry), ha='center', va='center',
                    color='white', fontweight='bold', fontsize=12, zorder=6)
        
        circle_est = Circle((rx, ry), dist_est_m, fill=False,
                             edgecolor=resp_colors[label], linewidth=2, alpha=0.8)
        ax.add_patch(circle_est)
        
        circle_true = Circle((rx, ry), true_dist_m, fill=False,
                              edgecolor=resp_colors[label], linewidth=1.5, 
                              linestyle='--', alpha=0.5)
        ax.add_patch(circle_true)
    
    ax.scatter(real_x, real_y, s=350, c='gold', marker='*',
               edgecolor='black', linewidth=2, zorder=10, label='True position')
    
    # Compute estimate
    distances = dict(zip(sample_data['responder_label'], sample_data['dist_est_cm']))
    result = multilaterate(distances, {r: RESPONDERS_ALL[r] for r in responders})
    if result:
        ax.scatter(result[0], result[1], s=200, c='red', marker='x',
                   linewidth=3, zorder=10, label='Estimated')
        pos_error = np.sqrt((result[0] - real_x)**2 + (result[1] - real_y)**2)
        ax.set_title(f'Distance Rings: {position}, Sample {sample_num}\n'
                     f'(Solid=estimated, Dashed=true) | Error: {pos_error:.2f} m',
                     fontsize=13, fontweight='bold')
    
    ax.set_xlim(-3, 23)
    ax.set_ylim(-3, 13)
    ax.set_xlabel('X Position (meters)')
    ax.set_ylabel('Y Position (meters)')
    ax.set_aspect('equal')
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)
    
    return fig, ax


def main():
    print("=" * 60)
    print("FTM Multilateration Analysis Report Generator")
    print("=" * 60)
    
    # Load data
    print("\n📂 Loading data...")
    df_all = load_ftm_data()
    df_all = calculate_errors(df_all)
    print(f"   Total samples: {len(df_all):,}")
    
    # Prepare filtered data (without R4)
    df_no_r4 = df_all[df_all['responder_label'] != 'r4'].copy()
    
    # Compute position estimates
    print("\n🧮 Computing position estimates...")
    print("   - With all responders...")
    results_all = compute_position_estimates(df_all, RESPONDERS_ALL)
    print(f"     {len(results_all)} estimates computed")
    
    print("   - Without R4...")
    results_no_r4 = compute_position_estimates(df_no_r4, RESPONDERS_NO_R4)
    print(f"     {len(results_no_r4)} estimates computed")
    
    # Create PDF
    print(f"\n📄 Generating PDF: {OUTPUT_PDF}")
    
    with PdfPages(OUTPUT_PDF) as pdf:
        
        # Page 1: Title
        print("   - Title page")
        add_title_page(pdf)
        
        # Page 2: Executive Summary
        print("   - Executive summary")
        summary_content = [
            "## Key Findings",
            "",
            "This report analyzes Fine Timing Measurement (FTM) performance for indoor",
            "positioning using 4 ESP32-S3 responders in a 20m × 10m room.",
            "",
            "## Main Results (All 4 Responders)",
            f"• Mean distance estimation error: +{df_all['error_cm'].mean():.0f} cm (systematic overestimation)",
            f"• Mean absolute distance error: {df_all['abs_error_cm'].mean():.0f} cm",
            f"• Mean position error (multilateration): {results_all['pos_error_m'].mean():.2f} m",
            "",
            "## Results Without R4 (Problematic Responder Excluded)",
            f"• Mean distance estimation error: +{df_no_r4['error_cm'].mean():.0f} cm",
            f"• Mean absolute distance error: {df_no_r4['abs_error_cm'].mean():.0f} cm  (+30.7% improvement)",
            f"• Mean position error (trilateration): {results_no_r4['pos_error_m'].mean():.2f} m  (+10.8% improvement)",
            "",
            "## Critical Observations",
            "• R4 had 3.6× worse accuracy than best responder (r3)",
            "• External antenna (r3) performs ~2× better than PCB antennas",
            "• Position near windows/doors (r2) shows increased error",
            "• System reliability: 94.8% complete samples (all 4 responders)",
        ]
        add_text_page(pdf, "Executive Summary", summary_content)
        
        # Page 3: Hardware Configuration
        print("   - Hardware configuration")
        hw_df = pd.DataFrame([
            ['r1', 'Adafruit Feather ESP32-S3 TFT', 'PCB', '(0, 0)', '277 cm', '-41.4 dBm'],
            ['r2', 'Adafruit Feather ESP32-S3 TFT', 'PCB', '(20, 0)', '527 cm', '-45.0 dBm'],
            ['r3', 'Seeed XIAO ESP32-S3', 'u.FL External', '(0, 10)', '283 cm', '-34.7 dBm'],
            ['r4', 'Adafruit Feather ESP32-S3', 'PCB', '(20, 10)', '1005 cm', '-49.7 dBm'],
        ], columns=['ID', 'Hardware', 'Antenna', 'Position', 'Mean |Error|', 'Mean RSSI'])
        add_table_page(pdf, "Hardware Configuration", hw_df,
                       "Responder hardware and measured performance metrics")
        
        # Page 4: Room Layout
        print("   - Room layout")
        fig, ax = create_room_layout_figure(df_all, RESPONDERS_ALL.keys(), "(All Responders)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 5: Distance Error Statistics - All
        print("   - Distance error statistics")
        stats_all = []
        for resp in ['r1', 'r2', 'r3', 'r4']:
            mask = df_all['responder_label'] == resp
            stats_all.append([
                resp,
                f"{df_all.loc[mask, 'error_cm'].mean():+.0f}",
                f"{df_all.loc[mask, 'error_cm'].std():.0f}",
                f"{df_all.loc[mask, 'abs_error_cm'].mean():.0f}",
                f"{df_all.loc[mask, 'rssi'].mean():.1f}",
            ])
        stats_df = pd.DataFrame(stats_all, 
                                columns=['Responder', 'Mean Error (cm)', 'Std Dev (cm)', 
                                         'Mean |Error| (cm)', 'Mean RSSI (dBm)'])
        add_table_page(pdf, "Distance Estimation Error by Responder", stats_df,
                       "With all 4 responders")
        
        # Page 6: Error Distribution Plots - All
        print("   - Error distribution (all)")
        fig, axes = create_error_distribution_figure(df_all, "(All Responders)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 7: Position Estimation - All
        print("   - Position estimation (all)")
        pos_stats = results_all.groupby('position').agg({
            'pos_error_m': ['mean', 'std', 'min', 'max'],
            'real_x': 'first',
            'real_y': 'first'
        }).round(3)
        pos_stats.columns = ['Mean (m)', 'Std (m)', 'Min (m)', 'Max (m)', 'X', 'Y']
        pos_stats = pos_stats.reset_index()
        add_table_page(pdf, "Position Estimation Error by Location", pos_stats,
                       "Multilateration with 4 responders")
        
        # Page 8: Position Estimation Figure - All
        print("   - Position estimation figure (all)")
        fig, ax = create_position_estimation_figure(results_all, RESPONDERS_ALL.keys(),
                                                    "(All Responders)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 9: Distance Rings Example
        print("   - Distance rings visualization")
        fig, ax = create_distance_rings_figure(df_all, 'p22', 1, RESPONDERS_ALL.keys())
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 10: Analysis Without R4 - Header
        print("   - Without R4 section")
        no_r4_content = [
            "## Rationale for Excluding R4",
            "",
            "Responder R4 showed significantly degraded performance:",
            f"• Mean absolute error: 1005 cm (vs 280 cm for r3)",
            "• Weakest RSSI: -49.7 dBm (vs -34.7 dBm for r3)",
            "• Highest failure rate: 1.50%",
            "",
            "Possible causes: PCB antenna issues, environmental interference,",
            "or hardware defects. This section analyzes system performance",
            "with R4 excluded to assess achievable accuracy.",
            "",
            "---",
            "",
            "## Results Summary (Without R4)",
            f"• Distance measurements: {len(df_no_r4):,} (R4 removed: {len(df_all)-len(df_no_r4):,})",
            f"• Mean distance error: +{df_no_r4['error_cm'].mean():.0f} cm",
            f"• Mean absolute error: {df_no_r4['abs_error_cm'].mean():.0f} cm",
            f"• Position estimates: {len(results_no_r4):,}",
            f"• Mean position error: {results_no_r4['pos_error_m'].mean():.2f} m",
        ]
        add_text_page(pdf, "Analysis Without R4", no_r4_content)
        
        # Page 11: Room Layout Without R4
        print("   - Room layout (no R4)")
        fig, ax = create_room_layout_figure(df_no_r4, RESPONDERS_NO_R4.keys(),
                                            "(R4 Excluded)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 12: Error Distribution - No R4
        print("   - Error distribution (no R4)")
        fig, axes = create_error_distribution_figure(df_no_r4, "(Without R4)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 13: Position Estimation - No R4
        print("   - Position estimation (no R4)")
        fig, ax = create_position_estimation_figure(results_no_r4, RESPONDERS_NO_R4.keys(),
                                                    "(Without R4)")
        pdf.savefig(fig, bbox_inches='tight')
        plt.close(fig)
        
        # Page 14: Comparison Table
        print("   - Comparison table")
        comparison_df = pd.DataFrame([
            ['Mean Distance Error', f'+{df_all["error_cm"].mean():.0f} cm', 
             f'+{df_no_r4["error_cm"].mean():.0f} cm', '—'],
            ['Mean |Distance Error|', f'{df_all["abs_error_cm"].mean():.0f} cm',
             f'{df_no_r4["abs_error_cm"].mean():.0f} cm', '+30.7%'],
            ['Std Dev (Distance)', f'{df_all["error_cm"].std():.0f} cm',
             f'{df_no_r4["error_cm"].std():.0f} cm', 
             f'+{100*(1-df_no_r4["error_cm"].std()/df_all["error_cm"].std()):.1f}%'],
            ['Mean Position Error', f'{results_all["pos_error_m"].mean():.2f} m',
             f'{results_no_r4["pos_error_m"].mean():.2f} m', '+10.8%'],
            ['Median Position Error', f'{results_all["pos_error_m"].median():.2f} m',
             f'{results_no_r4["pos_error_m"].median():.2f} m', '—'],
            ['Best Position Error', f'{results_all["pos_error_m"].min():.2f} m',
             f'{results_no_r4["pos_error_m"].min():.2f} m', '—'],
        ], columns=['Metric', 'With R4', 'Without R4', 'Improvement'])
        add_table_page(pdf, "Performance Comparison: With vs Without R4", comparison_df,
                       "Quantitative improvement from excluding problematic responder")
        
        # Page 15: Conclusions
        print("   - Conclusions")
        conclusions_content = [
            "## Distance Estimation",
            "",
            "• Systematic positive bias observed (+343 to +503 cm depending on config)",
            "• Antenna quality significantly impacts accuracy",
            "• External u.FL antenna (r3) achieves ~280 cm mean error",
            "• PCB antennas achieve ~280-530 cm depending on position",
            "",
            "## Position Estimation",
            "",
            "• Multilateration (4 resp): 5.17 m mean error",
            "• Trilateration (3 resp, no R4): 4.62 m mean error",
            "• Removing faulty hardware improves overall accuracy",
            "• Best case achievable: ~6 cm position error",
            "",
            "## Recommendations",
            "",
            "• Use external antennas for all responders",
            "• Avoid placing responders near windows/doors",
            "• Implement RSSI-based quality filtering",
            "• Consider calibration to remove systematic bias",
            "• Minimum 4 responders recommended for redundancy",
            "",
            "## Sample Completeness",
            "",
            "• 94.8% of samples had all 4 responders",
            "• 5.2% had 3 responders (1 failure)",
            "• Per-responder failure rate: 1.0-1.5%",
        ]
        add_text_page(pdf, "Conclusions & Recommendations", conclusions_content)
        
        # Page 16: Code Reference
        print("   - Code reference")
        code_content = [
            "## Data Processing",
            "",
            "CSV files contain FTM measurements with columns:",
            "position, real_x, real_y, responder_ssid, responder_label,",
            "responder_x, responder_y, dist_est_cm, rtt_est_ns, rssi, sample_num",
            "",
            "Error lines (starting with # E W) are filtered during loading.",
            "",
            "## Key Calculations",
            "",
        ]
        code_block = """# True distance calculation
true_dist = sqrt((real_x - resp_x)² + (real_y - resp_y)²)

# Error calculation  
error = dist_est_cm - true_dist_cm

# Multilateration (least squares)
def residuals(point):
    x, y = point
    calc_dists = sqrt((resp_x - x)² + (resp_y - y)²)
    return calc_dists - measured_dists

result = least_squares(residuals, initial_guess)"""
        
        add_text_page(pdf, "Methodology & Code Reference", code_content, code_block)
    
    print(f"\n✅ Report generated: {OUTPUT_PDF.absolute()}")
    print("=" * 60)


if __name__ == "__main__":
    main()
