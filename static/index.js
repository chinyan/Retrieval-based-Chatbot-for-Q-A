var state = 0;
var chat = "";

  class chat_control{
    constructor(){
        this.msg_list = $('.msg-group');
        console.log(this.msg_list);
        this.message = '';
        this.response = '';
        this.top_five = [];
    }

    send_msg(name,msg){
      this.msg_list.append(this.get_msg_html(name,msg,'right'));
      this.scroll_to_bottom();
    }

    receive_msg(name,msg){
      this.msg_list.append(this.get_msg_html(name,msg,'left'));
      this.scroll_to_bottom();
    }

    get_msg_html(name, msg, side){
      var msg_temple = `
        <div class="card">
          <div class="card-body">
              <h6 class="card-subtitle mb-2 text-muted text-${side}">${name}</h6>
              <p class="card-text float-${side}">${msg}</p>
          </div>
        </div>
        `;
        return msg_temple;
    }

    scroll_to_bottom(){
      this.msg_list.scrollTop(this.msg_list[0].scrollHeight);
    }
  }

function language(){
  language  = $("#language").val();
  console.log("language");
  d3.xhr("/get_language/")
  .header("Content-Type" , "application/json")
  .post(
    JSON.stringify(language),
    function(err, rawData){

      var data = JSON.parse(rawData.response);
      console.log(data);
    })};

function typein(){
  var input_box = $('#input-box');

  function handle_msg(msg){
    msg = msg.trim();
    return msg
  }

  function send_msg(){
    msg = handle_msg(input_box.val());
    console.log(msg);

    if (msg !=''){
      chat.send_msg('You', msg);
      console.log("msg is not null")
      var input = {"MESSAGE":input_box.val()}
      input_box.val('');

      console.log("input")
      console.log(input)

      setTimeout(function(){
        d3.xhr("/get_message/")
          .header("Content-Type" , "application/json")
          .post(
            JSON.stringify(input),
            function(err, rawData){
              var data = JSON.parse(rawData.response);
              var message = data["MESSAGE"];
              var response = data["RESPONSE"]
              var top_five = data["TOP_FIVE"];
              console.log(message);
              console.log(response);
              console.log(top_five);
              chat.message = message;
              chat.response = response;
              chat.top_five = top_five;

              if(top_five.length == 0){
                chat.receive_msg('Chatbot-Pipi',chat.message);
                chat.receive_msg('Chatbot-Pipi','Please ask me a Stack Overflow question ...');
              }else{
                var helpful = "Was this answer helpful? Yes/No"
                var best = "The most relevant question and answer is: " + "<br>" + "<br>";
                best += "Q: " + chat.message + "<br>";
                best += "A: " + chat.response;
                chat.receive_msg('Chatbot-Pipi', best);
                chat.receive_msg('Chatbot-Pipi', helpful);
                state = 1;
              }

            },1000);
      }
      );
      MathJax.Hub.Queue(["Typeset",MathJax.Hub]);
    }
  }

function box_key_pressing(){
    console.log(state);
    switch (state){
      case 0:
      send_msg();

      break;

      case 1:
      var check = input_box.val().toLowerCase();
      chat.send_msg('You', check);
      if(check == "no"){
        var text = "";
        console.log(chat.top_five)
        for (var i = 0; i < chat.top_five.length; i++) {
            text += (i+1) + ". ";
            text += chat.top_five[i]['MESSAGE'] + "<br>";
        }
        text += "<br>" + "Please enter the question number you find most relevant: " + "<br>";
        chat.receive_msg('Chatbot-Pipi', text);
        state = 2
      } else if(check == "yes"){
            var default_message = "Hi, I'm Chatbot-Pipi. What can i do for you?";
            chat.receive_msg('Chatbot-Pipi', default_message);
            state = 0
      } else{
            var yes_no_message = "Please type Yes/No ..."
            chat.receive_msg('Chatbot-Pipi', yes_no_message);
      }
      input_box.val('');
      break;

      case 2:
        chat.send_msg('You', input_box.val());

        var check = parseInt(input_box.val());
        if(!isNaN(check) && (check <= chat.top_five.length) && (check > 0)){
            var text = chat.top_five[check-1]['RESPONSE'];
            chat.receive_msg('Chatbot-Pipi', text);

            var read_more_message = "Would you like to read another questions? Yes/No";
            chat.receive_msg('Chatbot-Pipi', read_more_message);
            state = 3;
        } else{
            var text = "Please input a valid integer from 1 to " + chat.top_five.length + " ...";
            chat.receive_msg('Chatbot-Pipi', text);
        }


        input_box.val('');
        break;

      case 3:
        chat.send_msg('You', input_box.val());
        var check = input_box.val().toLowerCase();
        if(typeof input_box.val() == 'string'){
            if(input_box.val() == "no"){
                var default_message = "Hi, I'm Chatbot-Pipi. What can i do for you?";
                chat.receive_msg('Chatbot-Pipi', default_message);
                state = 0;
            } else if(input_box.val() == "yes"){
                var default_message = "Please enter the another question number you are interested: ";
                chat.receive_msg('Chatbot-Pipi', default_message);
                state = 2;
            } else{
                var yes_no_message = "Please type Yes/No ..."
                chat.receive_msg('Chatbot-Pipi', yes_no_message);
            }
        }
        input_box.val('');
        break;

    }
  }

  box_key_pressing();
};

 $(document).ready(function() {
 chat = new chat_control()
 $('#input-box').focus();
})
