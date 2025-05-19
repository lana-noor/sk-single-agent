import matplotlib.pyplot as plt
import base64
from io import BytesIO
from semantic_kernel.functions import kernel_function

class FundPlotPlugin:

    @kernel_function(name="generate_fund_plot", description="Generate a financial trend plot for selected metric.")
    def generate_fund_plot(self, x_axis: list, y_data: list, y_label: str) -> str:
        """
        Generates a matplotlib line plot from given data and returns base64 image string.
        x_axis: List of x values (e.g., years)
        y_data: List of y values (e.g., NAV)
        y_label: Label for y-axis (e.g., Net Asset Value)
        """
        fig, ax = plt.subplots()
        ax.plot(x_axis, y_data, marker='o')
        ax.set_xlabel("Year")
        ax.set_ylabel(y_label)
        ax.set_title(f"{y_label} Over Time")
        ax.grid(True)

        buf = BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        img_base64 = base64.b64encode(buf.read()).decode('utf-8')
        plt.close()

        return f"data:image/png;base64,{img_base64}"
