"""
Chart generation logic for Analytics Dashboard Helper package.
Creates interactive Plotly visualizations.
"""

import logging
from typing import Dict, List, Any

import plotly.graph_objects as go
import plotly.express as px

from .config import ChartConfig

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates interactive Plotly charts for analytics."""

    def __init__(self, config: ChartConfig):
        self.config = config

        # Soft professional blue gradient for email status charts
        self.email_status_palette = [
            "#cfe2ff",
            "#9ec5fe",
            "#6ea8fe",
            "#3d8bfd",
            "#0d6efd",
        ]

    # -------------------------------------------------------------------------
    # Qualified vs Disqualified
    # -------------------------------------------------------------------------
    def create_qualified_disqualified_bar_chart(self, data: Dict[str, int]) -> go.Figure:
        """
        Create a bar chart comparing Qualified vs Disqualified counts.
        """
        try:
            categories = list(data.keys())
            values = list(data.values())

            colors = ["#28a745", "#dc3545"]  # Green for Qualified, Red for Disqualified

            fig = go.Figure(
                data=[
                    go.Bar(
                        x=categories,
                        y=values,
                        text=values,
                        textposition="auto",
                        marker_color=colors,
                        hovertemplate="<b>%{x}</b><br>Count: %{y}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "Qualified vs Disqualified (Bar)",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                xaxis_title="Status",
                yaxis_title="Count",
                template=self.config.TEMPLATE,
                showlegend=False,
                height=self.config.DEFAULT_HEIGHT,
                width=self.config.DEFAULT_WIDTH,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info("Created qualified vs disqualified bar chart")
            return fig

        except Exception as e:
            logger.error(f"Error creating bar chart: {str(e)}")
            raise

    def create_qualified_disqualified_pie_chart(
        self, data: Dict[str, int]
    ) -> go.Figure:
        """
        Create a pie chart for Qualified vs Disqualified.
        """
        try:
            labels = list(data.keys())
            values = list(data.values())
            colors = ["#28a745", "#dc3545"]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        marker=dict(colors=colors),
                        textinfo="label+percent",
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "Qualified vs Disqualified (Pie)",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                template=self.config.TEMPLATE,
                showlegend=True,
                height=self.config.DONUT_SIZE,
                width=self.config.DONUT_SIZE,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info("Created qualified vs disqualified pie chart")
            return fig

        except Exception as e:
            logger.error(f"Error creating qualified vs disqualified pie chart: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    # DQ Reason Charts
    # -------------------------------------------------------------------------
    def create_dq_reason_bar_chart(
        self, reason_counts: Dict[str, int], top_n: int = 10
    ) -> go.Figure:
        """
        Create a horizontal bar chart for top DQ reasons.
        """
        try:
            sorted_reasons = sorted(
                reason_counts.items(), key=lambda x: x[1], reverse=True
            )[:top_n]
            reasons = [item[0] for item in sorted_reasons]
            counts = [item[1] for item in sorted_reasons]

            # Reverse for better visualization (highest at top)
            reasons.reverse()
            counts.reverse()

            fig = go.Figure(
                data=[
                    go.Bar(
                        y=reasons,
                        x=counts,
                        orientation="h",
                        text=counts,
                        textposition="auto",
                        marker_color="#ff7f0e",
                        hovertemplate="<b>%{y}</b><br>Count: %{x}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": f"Top {len(reasons)} DQ Reasons (Bar)",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                xaxis_title="Count",
                yaxis_title="DQ Reason",
                template=self.config.TEMPLATE,
                showlegend=False,
                height=max(self.config.DEFAULT_HEIGHT, len(reasons) * 40),
                width=self.config.DEFAULT_WIDTH,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info(f"Created DQ reason bar chart with {len(reasons)} reasons")
            return fig

        except Exception as e:
            logger.error(f"Error creating DQ reason chart: {str(e)}")
            raise

    def create_dq_reason_pie_chart(
        self, reason_counts: Dict[str, int], top_n: int = 10
    ) -> go.Figure:
        """
        Create a pie chart for top DQ reasons.
        """
        try:
            sorted_reasons = sorted(
                reason_counts.items(), key=lambda x: x[1], reverse=True
            )[:top_n]
            labels = [item[0] for item in sorted_reasons]
            values = [item[1] for item in sorted_reasons]

            # Colorful palette for DQ reasons
            base_colors = px.colors.qualitative.Set3
            if len(labels) <= len(base_colors):
                colors = base_colors[: len(labels)]
            else:
                colors = (base_colors * (len(labels) // len(base_colors) + 1))[
                    : len(labels)
                ]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        marker=dict(colors=colors),
                        textinfo="label+percent",
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": f"Top {len(labels)} DQ Reasons (Pie)",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                template=self.config.TEMPLATE,
                showlegend=True,
                height=self.config.DONUT_SIZE,
                width=self.config.DONUT_SIZE,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info(f"Created DQ reason pie chart with {len(labels)} reasons")
            return fig

        except Exception as e:
            logger.error(f"Error creating DQ reason pie chart: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    # Email Status – Blue Gradient Donut
    # -------------------------------------------------------------------------
    def create_email_status_donut_chart(
        self, email_status_counts: Dict[str, int]
    ) -> go.Figure:
        """
        Create a donut chart for email status distribution.
        Uses a soft professional blue gradient palette.
        """
        try:
            labels = list(email_status_counts.keys())
            values = list(email_status_counts.values())

            # Build blue gradient colors
            base = self.email_status_palette
            if len(labels) <= len(base):
                colors = base[: len(labels)]
            else:
                colors = (base * (len(labels) // len(base) + 1))[: len(labels)]

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        hole=0.4,
                        marker=dict(colors=colors),
                        textinfo="label+percent",
                        textposition="outside",
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "Email Status - Qualified Leads",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                template=self.config.TEMPLATE,
                showlegend=True,
                legend=dict(
                    orientation="v",
                    yanchor="middle",
                    y=0.5,
                    xanchor="left",
                    x=1.05,
                ),
                height=self.config.DONUT_SIZE,
                width=self.config.DONUT_SIZE,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info(
                f"Created email status donut chart with {len(labels)} categories (blue gradient)"
            )
            return fig

        except Exception as e:
            logger.error(f"Error creating donut chart: {str(e)}")
            raise

    # -------------------------------------------------------------------------
    # Segment Charts
    # -------------------------------------------------------------------------
    def create_segment_pie_chart(self, segment_data: List[List[Any]]) -> go.Figure:
        """
        Create a pie chart for segment distribution.
        segment_data: table from analytics generator (header + rows incl. Grand Total)
        """
        try:
            # Extract data (skip header and grand total row)
            if len(segment_data) <= 2:
                # Not enough data
                labels = []
                values = []
            else:
                labels = [row[0] for row in segment_data[1:-1]]
                values = [row[3] for row in segment_data[1:-1]]  # Total column

            fig = go.Figure(
                data=[
                    go.Pie(
                        labels=labels,
                        values=values,
                        textinfo="label+percent",
                        hovertemplate="<b>%{label}</b><br>Count: %{value}<br>Percentage: %{percent}<extra></extra>",
                    )
                ]
            )

            fig.update_layout(
                title={
                    "text": "Segment Distribution",
                    "font": {
                        "size": self.config.TITLE_FONT_SIZE,
                        "family": self.config.FONT_FAMILY,
                    },
                    "x": 0.5,
                    "xanchor": "center",
                },
                template=self.config.TEMPLATE,
                showlegend=True,
                height=self.config.DONUT_SIZE,
                width=self.config.DONUT_SIZE,
                font={
                    "family": self.config.FONT_FAMILY,
                    "size": self.config.LABEL_FONT_SIZE,
                },
            )

            logger.info("Created segment pie chart")
            return fig

        except Exception as e:
            logger.error(f"Error creating segment pie chart: {str(e)}")
            raise
