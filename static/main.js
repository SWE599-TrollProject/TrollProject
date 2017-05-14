(function ($) {

    $('.bot.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#ff1e41', '#ff5f43']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    $('.activity.circle').circleProgress({
        value: 0,
        lineCap: 'round'
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(3));
    });

    $('.toxicity.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#ff1e41', '#ff5f43']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });


    $('.spam.circle').circleProgress({
        value: 0,
        lineCap: 'round'
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });


    $('.inflammatory.circle').circleProgress({
        value: 0,
        lineCap: 'round',
        fill: {gradient: ['#0681c4', '#4ac5f8']}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    $('.obscenity.circle').circleProgress({
        startAngle: -Math.PI / 4 * 3,
        value: 0,
        lineCap: 'round',
        fill: {color: '#ffa500'}
    }).on('circle-animation-progress', function (event, progress, stepValue) {
        $(this).find('strong').text(stepValue.toFixed(2).substr(2));
    });

    var form = $('#searchForm');
    form.submit(function (e) {
        e.preventDefault();
        $.ajax({
            type: "POST",
            url: "/search",
            data: form.serialize(),
            success: function (data) {
                var bot = $('.bot.circle');
                var activity = $('.activity.circle');
                var toxicity = $('.toxicity.circle');
                var spam = $('.spam.circle');
                var inflammatory = $('.inflammatory.circle');
                var obscenity = $('.obscenity.circle');

                var r = JSON.parse(data).result;
                if (r === "inactive"){
                    var alert = $(".error-alert");
                    alert.html("this user is totally inactive");
                    alert.fadeIn("slow");
                    window.setTimeout(
                        function() { alert.fadeOut("slow"); }, 5000
                    );
                }
                toxicity.circleProgress({value: r.troll_level.TOXICITY});
                spam.circleProgress({value: r.troll_level.SPAM});
                inflammatory.circleProgress({value: r.troll_level.INFLAMMATORY});
                obscenity.circleProgress({value: r.troll_level.OBSCENE});

                var show_activity_as = r.activity_level.tweets_per_day;
                if (r.activity_level.tweets_per_day > 1) {
                    show_activity_as = 1;
                }

                activity.circleProgress({value: show_activity_as});
                bot.circleProgress({value: r.bot_level.suspect_rate});
            },
            error: function (data) {
                var alert = $(".error-alert");
                var err = data.responseJSON.message[0];
                alert.html(err.message);
                alert.fadeIn("slow");
                window.setTimeout(
                    function() { alert.fadeOut("slow"); }, 5000
                );
            }
        });
    })

})(jQuery);