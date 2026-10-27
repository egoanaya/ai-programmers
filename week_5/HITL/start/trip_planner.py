"""
Trip Planning System with Human-in-the-Loop

This script demonstrates a simple HITL system for planning a trip with three steps:
1. Destination selection with LLM suggestion
2. Flight selection with LLM suggestion
3. Itinerary generation with LLM suggestion

Each step includes human verification and modification options.
"""

import json
from typing import Dict, Optional, List
from dataclasses import dataclass
from openai import OpenAI
import os
from pydantic import BaseModel, Field

@dataclass
class TripPlan:
    """Represents a complete trip plan."""
    destination: str
    departure_city: str
    flight_info: Dict
    itinerary: Dict

class FlightInfo(BaseModel):
    """Model for flight information."""
    flight_number: str = Field(description="Flight number")
    departure_time: str = Field(description="Departure time in HH:MM format")
    arrival_time: str = Field(description="Arrival time in HH:MM format")
    airline: str = Field(description="Name of the airline")

class Itinerary(BaseModel):
    """Model for daily itinerary."""
    daily_activities: List[List[str]] = Field(description="List of activities for each day of the trip")

class TripPlanner:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.trip_plan = None

    def suggest_destination(self) -> str:
        """Use LLM to suggest a travel destination."""
        prompt = """Suggest an interesting travel destination. 
        Consider factors like weather, tourist attractions, and cultural experiences.
        Return only the destination name, nothing else."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini-2024-07-18",
                messages=[
                    {"role": "system", "content": "You are a helpful travel assistant."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error getting destination suggestion: {e}")
            return "Paris"  # Fallback destination

    def suggest_flight(self, departure_city: str, destination: str) -> FlightInfo:
        """Use LLM to suggest a fictional flight."""
        prompt = f"""Generate a fictional flight from {departure_city} to {destination}.
        Include departure time, arrival time, and flight number."""

        try:
            response = self.client.responses.parse(
                model="gpt-4o-mini-2024-07-18",
                input=[
                    {"role": "system", "content": "You are a helpful travel assistant."},
                    {"role": "user", "content": prompt}
                ],
                text_format=FlightInfo
            )
            return response.output_parsed
        except Exception as e:
            print(f"Error getting flight suggestion: {e}")
            return FlightInfo(
                flight_number="AA123",
                departure_time="10:00",
                arrival_time="12:00",
                airline="Example Airlines"
            )

    def generate_itinerary(self, destination: str) -> Itinerary:
        """Use LLM to generate a brief itinerary."""
        prompt = f"""Generate a brief 3-day itinerary for {destination}.
        Include 2-3 activities per day."""

        try:
            response = self.client.responses.parse(
                model="gpt-4o-mini-2024-07-18",
                input=[
                    {"role": "system", "content": "You are a helpful travel assistant."},
                    {"role": "user", "content": prompt}
                ],
                text_format=Itinerary
            )
            return response.output_parsed
        except Exception as e:
            print(f"Error generating itinerary: {e}")
            return Itinerary(
                daily_activities=[
                    ["Morning activity", "Afternoon activity"],
                    ["Morning activity", "Afternoon activity"],
                    ["Morning activity", "Afternoon activity"]
                ]
            )

    def get_human_confirmation(self, prompt: str) -> bool:
        """Get human confirmation for a suggestion."""
        while True:
            choice = input(f"{prompt} (y/n): ").lower().strip()
            if choice in ['y', 'n']:
                return choice == 'y'
            print("Please enter 'y' or 'n'")

    def plan_trip(self) -> None:
        """Run the complete trip planning process."""
        print("\n=== Welcome to the Trip Planner! ===\n")

        ## TODO Decide which steps would benefit from a human-in-the-loop experience.
        # Use get_human_confirmation to stop the flow and ask the human a question.

        # Step 1: Destination Selection
        suggested_destination = self.suggest_destination()
        print(f"\nSuggested destination: {suggested_destination}")
        
        # Example
        if self.get_human_confirmation("Would you like to use this destination?"):
            destination = suggested_destination
        else:
            destination = input("Enter your preferred destination: ").strip()
        
        # Step 2: Flight Selection
        departure_city = input("\nEnter your departure city: ").strip()
        suggested_flight = self.suggest_flight(departure_city, destination)
        
        print("\nSuggested flight:")
        print(f"Airline: {suggested_flight.airline}")
        print(f"Flight: {suggested_flight.flight_number}")
        print(f"Departure: {suggested_flight.departure_time}")
        print(f"Arrival: {suggested_flight.arrival_time}")
        
        # Human-in-the-loop: It will confirm or modify the suggested flight
        if self.get_human_confirmation("Would you like to use this flight?"):
            selected_flight = suggested_flight
        else:
            print("\nEnter your preferred flight details:")
            selected_flight = FlightInfo(
                airline=input("Airline: ").strip(),
                flight_number=input("Flight number: ").strip(),
                departure_time=input("Departure time (HH:MM): ").strip(),
                arrival_time=input("Arrival time (HH:MM): ").strip()
            )
        
        # Step 3: Itinerary Generation
        suggested_itinerary = self.generate_itinerary(destination)
        
        print("\nSuggested itinerary:")
        for index, activities in enumerate(suggested_itinerary.daily_activities, 1):
            print(f"\nDAY {index}:")
            for activity in activities:
                print(f"- {activity}")

        # Human-in-the-loop: It will confirm or customize the itinerary
        if self.get_human_confirmation("Would you like to use this itinerary?"):
            selected_itinerary = suggested_itinerary
        else:
            print("\nCustomize your 3-day itinerary:")
            daily_activities = []

            for day in range(1, 4):
                print(f"\nDay {day}:")
                activities = input(
                    "Enter activities separated by commas: "
                ).strip().split(",")

                daily_activities.append(
                    [activity.strip() for activity in activities if activity.strip()]
                )

            selected_itinerary = Itinerary(
                daily_activities=daily_activities
            )

        # Save the complete trip plan
        self.trip_plan = TripPlan(
            destination=destination,
            departure_city=departure_city,
            flight_info=selected_flight,
            itinerary=selected_itinerary
        )

        # Display final plan
        print("\n=== Your Trip Plan ===")
        print(f"Destination: {self.trip_plan.destination}")
        print(f"Departure from: {self.trip_plan.departure_city}")
        print("\nFlight Information:")
        print(f"Airline: {selected_flight.airline}")
        print(f"Flight: {selected_flight.flight_number}")
        print(f"Departure: {selected_flight.departure_time}")
        print(f"Arrival: {selected_flight.arrival_time}")
        print("\nItinerary:")
        for index, activities in enumerate(self.trip_plan.itinerary.daily_activities, 1):
            print(f"\nDAY {index}:")
            for activity in activities:
                print(f"- {activity}")

def main():
    planner = TripPlanner()
    planner.plan_trip()

if __name__ == "__main__":
    main() 