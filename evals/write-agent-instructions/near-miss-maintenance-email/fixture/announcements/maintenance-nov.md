Subject: Scheduled maintenance on Nov 15

Hi there,

We wanted to let you know that we are going to be doing some planned maintanence on our database infrastucture. This is so that we can upgrade to a newer version of Postgres which will make things faster and more reliable for everyone going forward.

The maintenance is happening on Sunday 15 November 2026 from 02:00 to 04:00 UTC. During this time the dashboard and the API will be in read-only mode, which means you can still view everything and make GET requests but you won't be able to create or change anything. Any webhooks that would of been sent during the window will be queued up and then delivered once we are done, so you won't miss any.

You don't need to do anything to prepare for this.

If you want to follow along you can check status.ferrybase.io where we'll post updates as we go.

Thanks for your patience and sorry for any inconvience this causes!

The Ferrybase team
