# Bookings Agent

Bookings Agent is an intelligent, modular system for managing appointment bookings, user screening, and calendar protection—designed for seamless integration with social media and modern web interfaces.

## Project Objective

The goal of this project is to automate and streamline the process of booking appointments, especially for users coming from social media platforms. It ensures only relevant, serious inquiries are allowed through, protects the owner's private time, and provides a professional, guided experience from first contact to confirmed booking.

## What's Available

### Backend (Python, FastAPI, Google ADK)

- **Root Booking Guide Agent**: Orchestrates the booking flow, screens users, manages session progression, and handles calendar logic.
- **Sub-Agents**:
  - **Booking Validator**: Screens users for topic relevance and seriousness before showing available slots.
  - **Inquiry Collector**: Collects general inquiries and saves them to Firestore, without promising a reply.
  - **Payment Agent**: Handles Paystack payment sessions and webhook verification for paid bookings.
- **Firestore Integration**: Stores user preferences, booking details, validation results, and inquiries in namespaced collections.
- **Calendar Management**: Integrates with Google Calendar to show only available slots, prevent double bookings, and respect blocked/private times.
- **API Endpoints**: Exposes endpoints for chat, payment webhooks, and payment status verification.
- **Deployment**: Designed for Google Cloud Run deployment, with local development supported via Firestore emulator and Makefile scripts.

### Frontend (Angular 19)

- **Modern Chat UI**: Provides a real-time chat interface for users to interact with the agent, view messages, and complete bookings.
- **Session Management**: Automatically creates and manages user sessions, supporting anonymous sign-in via Firebase.
- **Integration**: Communicates with the backend via a `/run` endpoint, with proxy configuration for local development.
- **Material Design**: Uses Angular Material for a polished, responsive user experience.

## System Architecture

- **Backend**: Python, FastAPI, Google ADK, Firestore, Google Calendar, Paystack integration.
- **Frontend**: Angular 19, Angular Material, Firebase Auth, RxJS.

## Key Features

- User screening and topic validation before showing available slots
- Private time and double booking protection
- Smart appointment suggestions and reminders
- Payment integration for paid bookings
- Inquiry collection for general requests

## Data Storage

- **Firestore Collections**:
  - `booking_memories`: Owner preferences, blocked times, recurring patterns
  - `booking_bookings`: Appointment details, status, user info
  - `booking_validations`: Validation and screening results
  - `inquiries`: General user inquiries

## Development & Deployment

- **Local Development**: Use the Firestore emulator and Makefile for running backend and frontend locally.
- **Cloud Deployment**: Deploy to Google Cloud Run using the provided Makefile.
- **Frontend**: Run with `npm start` in the `frontend/` directory.
- **Backend**: Run with `python main.py` (ensure Firestore credentials are set).

## Summary

Bookings Agent is a robust, extensible platform for managing appointment bookings with intelligent screening, calendar protection, and a modern chat-based frontend. It is suitable for professionals and businesses seeking to automate and secure their booking workflows, especially when handling high volumes of social media inquiries.
