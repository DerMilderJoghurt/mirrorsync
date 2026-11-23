package io.github.dermilderjoghurt.mirrorsync;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;

/** Re-plans the background check after a restart of the phone or an update of the app. */
public class BootReceiver extends BroadcastReceiver {
    @Override
    public void onReceive(Context context, Intent intent) {
        PollService.schedule(context);
    }
}
