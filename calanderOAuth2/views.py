from os import environ
from ossaudiodev import SNDCTL_COPR_SENDMSG
from django.shortcuts import render
import google_auth_oauthlib
from django.http import HttpResponseRedirect, JsonResponse
from rest_framework.views import APIView
from OAuth2.settings import CLIENT_SECRETS_FILE, SCOPES
from googleapiclient.discovery import build
from OAuth2.settings import env
from .utils import credentials_to_dict



class GoogleCalendarInitView(APIView):
    def get(self, request):
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, scopes=SCOPES)
        flow.redirect_uri = env('DOMAIN') + '/rest/v1/calendar/redirect'
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true')
        # Store the state so the callback can verify that the authorization
        # server response.
        request.session['state'] = state
        return HttpResponseRedirect(authorization_url)


class GoogleCalendarRedirectView(APIView):
    def get(self, request, format=None):
        # Step 2: Get an access token using the provided authorization code.
        flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
            CLIENT_SECRETS_FILE, SCOPES)

        flow.redirect_uri =  env('DOMAIN') + '/rest/v1/calendar/redirect'

        # Use the authorization server's response to fetch the OAuth 2.0 tokens.
        authorization_response = request.build_absolute_uri()
        flow.fetch_token(authorization_response=authorization_response)

        # Store credentials in the session.
        # ACTION ITEM: In a production app, you likely want to save these
        #              credentials in a persistent database instead.
        credentials = flow.credentials
        request.session['credentials'] = credentials_to_dict(credentials)

        # Get list of events from Google Calendar
        service = build('calendar', 'v3', credentials=credentials)
        events = service.events().list(calendarId='primary').execute()
        return JsonResponse(events)
