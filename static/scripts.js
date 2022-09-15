$( document ).ready(function() {
    //document.documentElement.requestFullscreen();
    

    var source = new EventSource('/stream');
    source.onmessage = function (event) {
        let d = JSON.parse(event.data);
        for (let i = 0; i < d.length; i++) {
            let e = d[i];
            if (e.updatetype == 'mesh') {
                document.getElementById('mesh').innerHTML = e.css;
            }
            else if (e.updatetype == 'calendar') {
                document.getElementById('schedule-container').innerHTML = e.html;
                document.getElementById('calendar-date').innerHTML = e.date;
                document.getElementById('calendar-weekday').innerHTML = e.weekday;
            }
            else if (e.updatetype == 'time') {
                document.getElementById('maintime').innerHTML = e.time;
            }
            else if (e.updatetype == 'spotify') {
                if (e.state != null) {
                    if (e.state == false) {
                        document.getElementById('pause-button').classList.add('hide');
                        document.getElementById('play-button').classList.remove('hide');
                    }
                    else {
                        document.getElementById('pause-button').classList.remove('hide');
                        document.getElementById('play-button').classList.add('hide');
                    }
                }
                if (e.albumcover) {
                    document.getElementById('spotify-image').src = e.albumcover;
                }
                if (e.name) {
                    document.getElementById('spotify-name').innerHTML = e.name;
                }
                if (e.artist) {
                    document.getElementById('spotify-artist').innerHTML = e.artist;
                }
                if (e.album) {
                    document.getElementById('spotify-album').innerHTML = e.album;
                }
                if (e.progress) {
                    document.getElementById('spotify-time').innerHTML = e.progress;
                }
                if (e.progressx) {
                    document.getElementById('spotify-progress').style.left = e.progressx;
                }
                if (e.length) {
                    document.getElementById('spotify-length').innerHTML = e.length;
                }
                if (e.shuffle != null) {
                    if (e.shuffle == true) {
                        document.getElementById('shuffle-button').classList.add('button-active');
                        document.getElementById('shuffle-button').classList.remove('button-inactive');
                    }
                    else {
                        document.getElementById('shuffle-button').classList.add('button-inactive');
                        document.getElementById('shuffle-button').classList.remove('button-active');
                    }
                }
                if (e.loop != null) {
                    if (e.loop === 'off') {
                        document.getElementById('loop-button').classList.add('button-inactive');
                        document.getElementById('loop-button').classList.remove('button-active');
                        document.getElementById('loop-button').classList.remove('hide');
                        document.getElementById('loop-button2').classList.add('hide');
                    }
                    else if (e.loop === 'context') {
                        document.getElementById('loop-button').classList.add('button-active');
                        document.getElementById('loop-button').classList.remove('button-inactive');
                        document.getElementById('loop-button').classList.remove('hide');
                        document.getElementById('loop-button2').classList.add('hide');
                    }
                    else if (e.loop === 'track') {
                        document.getElementById('loop-button').classList.add('hide');
                        document.getElementById('loop-button2').classList.remove('hide');

                    }
                }
                if (e.nextcover) {
                    document.getElementById('spotify-queue').src = e.nextcover;
                }
            }
            else if (e.updatetype == 'weather') {
                document.getElementById('current-temp').innerHTML = e.dicts[0].temp;
                document.getElementById('current-weather-icon').src = e.dicts[0].icon;
                for (let i = 1; i < e.dicts.length; i++) {
                    document.getElementById('temp-'+i).innerHTML = e.dicts[i].temp;
                    document.getElementById('time-'+i).innerHTML = e.dicts[i].time;
                    document.getElementById('icon-'+i).src       = e.dicts[i].icon;
                }
            }
        }
    };
});