import pandas as pd
import json
import os
import numpy as np
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from django.http import JsonResponse

# Custom JSON encoder function to handle NaN values
def handle_nan_values(data):
    """Process pandas dataframes to handle NaN values before JSON serialization"""
    if isinstance(data, dict):
        return {k: handle_nan_values(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [handle_nan_values(item) for item in data]
    elif isinstance(data, (pd.DataFrame, pd.Series)):
        return handle_nan_values(data.to_dict('records') if isinstance(data, pd.DataFrame) else data.to_dict())
    elif isinstance(data, np.ndarray):
        return handle_nan_values(data.tolist())
    elif isinstance(data, np.number):
        return None if np.isnan(data) or np.isinf(data) else float(data)
    elif pd.isna(data) or (isinstance(data, float) and (np.isnan(data) or np.isinf(data))):
        return None
    return data

# File path for the Excel data
EXCEL_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Sample_data.xlsx')

class ChatbotQueryView(APIView):
    def post(self, request):
        query = request.data.get('query', '').lower()
        
        # Read the Excel file
        try:
            df = pd.read_excel(EXCEL_FILE)
        except Exception as e:
            return Response(
                {"error": f"Error reading Excel file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        
        # Process the query
        response = self.process_query(query, df)
        # Process to handle NaN values
        processed_response = handle_nan_values(response)
        return Response(processed_response)
    
    def process_query(self, query, df):
        # Dynamically determine location column
        # Look for common location column names in the DataFrame
        possible_location_columns = ['final location', 'area', 'location', 'locality', 'region', 'zone']
        location_column = None
        for col in possible_location_columns:
            if col in df.columns:
                location_column = col
                break
        
        # If none found, use the first string column as a fallback
        if not location_column:
            for col in df.columns:
                if df[col].dtype == 'object' and df[col].nunique() > 5:
                    location_column = col
                    break
        
        # Dynamically determine year column
        year_column = None
        for col in df.columns:
            if col.lower() in ['year', 'yr']:
                year_column = col
                break
        
        # If no year column found, look for date-like columns
        if not year_column:
            for col in df.columns:
                if 'year' in col.lower() or 'date' in col.lower():
                    year_column = col
                    break
        
        # Find price and demand columns dynamically
        price_column = None
        demand_column = None
        
        for col in df.columns:
            col_lower = col.lower()
            if not price_column and ('price' in col_lower or 'rate' in col_lower) and pd.api.types.is_numeric_dtype(df[col]):
                price_column = col
            if not demand_column and ('sold' in col_lower or 'sales' in col_lower or 'demand' in col_lower or 'units' in col_lower) and pd.api.types.is_numeric_dtype(df[col]):
                demand_column = col
                
        # Extract area names from the query
        areas = []
        if location_column:
            all_areas = df[location_column].unique()
            for area in all_areas:
                if isinstance(area, str) and area.lower() in query:
                    areas.append(area)
        
        # If no specific areas mentioned, try to determine intent
        if not areas:
            if 'top' in query or 'best' in query:
                if year_column and location_column and demand_column:
                    recent_year = df[year_column].max()
                    top_areas = df[df[year_column] == recent_year].sort_values(demand_column, ascending=False).head(3)
                    
                    chart_data = {
                        'type': 'bar',
                        'labels': top_areas[location_column].tolist(),
                        'datasets': [{
                            'label': f'{demand_column}',
                            'data': top_areas[demand_column].tolist()
                        }]
                    }
                    
                    return {
                        'summary': f"Here are the top areas by demand for {recent_year}",
                        'chart_data': chart_data,
                        'table_data': top_areas.to_dict('records')
                    }
                else:
                    # Fallback if columns not found
                    return {
                        'summary': "Could not analyze data due to missing required columns.",
                        'chart_data': None,
                        'table_data': None
                    }
            
            # Default response if intent is unclear
            return {
                'summary': "I'm not sure what you're looking for. Please try specifying an area like 'Analyze Wakad' or 'Compare Aundh and Baner'.",
                'chart_data': None,
                'table_data': None
            }
        
        # Single area analysis
        if len(areas) == 1:
            area = areas[0]
            area_data = df[df[location_column] == area]
            
            # Check for specific time frame
            if 'last 3 years' in query or 'last three years' in query:
                if year_column:
                    max_year = df[year_column].max()
                    year_filter = [max_year - 2, max_year - 1, max_year]
                    area_data = area_data[area_data[year_column].isin(year_filter)]
            
            # Check if query is about price or demand specifically
            if 'price' in query and price_column:
                chart_data = {
                    'type': 'line',
                    'labels': area_data[year_column].tolist() if year_column else [],
                    'datasets': [{
                        'label': price_column,
                        'data': area_data[price_column].tolist()
                    }]
                }
                summary = f"Price trend analysis for {area}: "
                
                # Calculate price growth
                if len(area_data) > 1 and price_column:
                    area_data_sorted = area_data.sort_values(year_column) if year_column else area_data
                    first_price = area_data_sorted.iloc[0][price_column]
                    last_price = area_data_sorted.iloc[-1][price_column]
                    
                    # Handle NaN values
                    if pd.isna(first_price) or pd.isna(last_price):
                        growth = 0
                    elif first_price > 0:
                        growth = ((last_price - first_price) / first_price) * 100
                    else:
                        growth = 0
                    
                    # Use safe values for display
                    first_price = 0 if pd.isna(first_price) else first_price
                    last_price = 0 if pd.isna(last_price) else last_price
                    
                    summary += f"Prices have {'increased' if growth > 0 else 'decreased'} by {abs(growth):.1f}% "
                    summary += f"from {first_price:.2f} to {last_price:.2f}."
                
            elif 'demand' in query and demand_column:
                chart_data = {
                    'type': 'line',
                    'labels': area_data[year_column].tolist() if year_column else [],
                    'datasets': [{
                        'label': demand_column,
                        'data': area_data[demand_column].tolist()
                    }]
                }
                summary = f"Demand trend analysis for {area}: "
                
                if len(area_data) > 1 and demand_column:
                    area_data_sorted = area_data.sort_values(year_column) if year_column else area_data
                    first_demand = area_data_sorted.iloc[0][demand_column]
                    last_demand = area_data_sorted.iloc[-1][demand_column]
                    
                    # Handle NaN values
                    if pd.isna(first_demand) or pd.isna(last_demand):
                        change = 0
                    else:
                        change = last_demand - first_demand
                    
                    # Use safe values for display
                    first_demand = 0 if pd.isna(first_demand) else first_demand
                    last_demand = 0 if pd.isna(last_demand) else last_demand
                    
                    summary += f"Demand has {'increased' if change > 0 else 'decreased'} by {abs(change)} units "
                    summary += f"from {first_demand} to {last_demand} units sold."
            
            # Default to a general analysis
            else:
                # Initialize datasets for chart
                datasets = []
                
                # Add price data if available
                if price_column:
                    datasets.append({
                        'label': price_column,
                        'data': area_data[price_column].tolist(),
                        'yAxisID': 'y-price'
                    })
                
                # Add demand data if available
                if demand_column:
                    datasets.append({
                        'label': demand_column,
                        'data': area_data[demand_column].tolist(),
                        'yAxisID': 'y-demand'
                    })
                
                chart_data = {
                    'type': 'line',
                    'labels': area_data[year_column].tolist() if year_column else [],
                    'datasets': datasets,
                    'options': {
                        'scales': {
                            'y-price': {
                                'position': 'left',
                                'title': 'Price'
                            },
                            'y-demand': {
                                'position': 'right',
                                'title': 'Demand'
                            }
                        }
                    }
                }
                
                # Calculate averages for summary
                summary = f"Analysis of {area}: "
                
                if price_column:
                    avg_price = area_data[price_column].mean()
                    if not pd.isna(avg_price):
                        summary += f"Average price is ₹{avg_price:.2f} "
                
                if demand_column:
                    avg_demand = area_data[demand_column].mean()
                    if not pd.isna(avg_demand):
                        summary += f"with an average of {avg_demand:.1f} units sold. "
                
                # Add trend analysis if multiple data points
                if len(area_data) > 1:
                    area_data_sorted = area_data.sort_values(year_column) if year_column else area_data
                    
                    if price_column:
                        first_price = area_data_sorted.iloc[0][price_column]
                        last_price = area_data_sorted.iloc[-1][price_column]
                        
                        if not (pd.isna(first_price) or pd.isna(last_price)) and first_price > 0:
                            price_change = ((last_price - first_price) / first_price) * 100
                            summary += f"Over time, prices have {'increased' if price_change > 0 else 'decreased'} "
                            summary += f"by {abs(price_change):.1f}% "
                    
                    if demand_column:
                        first_demand = area_data_sorted.iloc[0][demand_column]
                        last_demand = area_data_sorted.iloc[-1][demand_column]
                        
                        if not (pd.isna(first_demand) or pd.isna(last_demand)):
                            demand_change = last_demand - first_demand
                            summary += f"and units sold have {'increased' if demand_change > 0 else 'decreased'} "
                            summary += f"by {abs(demand_change):.1f} units."
            
            return {
                'summary': summary,
                'chart_data': chart_data,
                'table_data': area_data.to_dict('records')
            }
        
        # Comparison between multiple areas
        elif len(areas) > 1:
            filtered_data = df[df[location_column].isin(areas)]
            
            if 'demand' in query and demand_column and year_column:
                # Compare demand trends
                pivot_data = filtered_data.pivot(index=year_column, columns=location_column, values=demand_column).reset_index()
                chart_datasets = []
                
                for area in areas:
                    if area in pivot_data:
                        chart_datasets.append({
                            'label': area,
                            'data': pivot_data[area].tolist()
                        })
                    else:
                        chart_datasets.append({
                            'label': area,
                            'data': []
                        })
                
                chart_data = {
                    'type': 'line',
                    'labels': pivot_data[year_column].tolist(),
                    'datasets': chart_datasets
                }
                
                # Generate summary comparing latest demand scores
                latest_year = filtered_data[year_column].max() if year_column in filtered_data.columns else None
                summary = f"Comparing demand trends between {', '.join(areas)}. "
                
                if latest_year:
                    latest_data = filtered_data[filtered_data[year_column] == latest_year]
                    
                    summary_parts = []
                    for area in areas:
                        area_demand = latest_data[latest_data[location_column] == area][demand_column].values
                        if len(area_demand) > 0 and not pd.isna(area_demand[0]):
                            summary_parts.append(f"{area}: {area_demand[0]} units")
                    
                    if summary_parts:
                        summary += f"Latest demand figures ({latest_year}): "
                        summary += ", ".join(summary_parts)
            
            elif price_column and year_column:
                # Default to price comparison
                pivot_data = filtered_data.pivot(index=year_column, columns=location_column, values=price_column).reset_index()
                chart_datasets = []
                
                for area in areas:
                    if area in pivot_data:
                        chart_datasets.append({
                            'label': area,
                            'data': pivot_data[area].tolist()
                        })
                    else:
                        chart_datasets.append({
                            'label': area,
                            'data': []
                        })
                
                chart_data = {
                    'type': 'line',
                    'labels': pivot_data[year_column].tolist(),
                    'datasets': chart_datasets
                }
                
                # Generate summary comparing latest prices
                latest_year = filtered_data[year_column].max() if year_column in filtered_data.columns else None
                summary = f"Comparing {', '.join(areas)}. "
                
                if latest_year:
                    latest_data = filtered_data[filtered_data[year_column] == latest_year]
                    
                    summary_parts = []
                    for area in areas:
                        area_price = latest_data[latest_data[location_column] == area][price_column].values
                        if len(area_price) > 0 and not pd.isna(area_price[0]):
                            summary_parts.append(f"{area}: ₹{area_price[0]:.2f}")
                    
                    if summary_parts:
                        summary += f"Latest prices ({latest_year}): "
                        summary += ", ".join(summary_parts)
            else:
                chart_data = None
                summary = f"Comparing {', '.join(areas)}, but could not find suitable data for comparison."
            
            return {
                'summary': summary,
                'chart_data': chart_data,
                'table_data': filtered_data.to_dict('records')
            }


class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)
    
    def post(self, request):
        file_obj = request.FILES.get('file', None)
        if not file_obj:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            # Save the file temporarily
            file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Sample_data.xlsx')
            with open(file_path, 'wb+') as destination:
                for chunk in file_obj.chunks():
                    destination.write(chunk)
                    
            # Try to read the file to verify it's a valid Excel file
            df = pd.read_excel(file_path)
            row_count = len(df)
            
            # Get column info for feedback
            column_info = []
            for col in df.columns:
                col_type = "numeric" if pd.api.types.is_numeric_dtype(df[col]) else "text"
                column_info.append({"name": col, "type": col_type})
            
            return Response({
                "message": f"File uploaded successfully with {row_count} records",
                "filename": file_obj.name,
                "columns": column_info
            })
            
        except Exception as e:
            return Response({
                "error": str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
