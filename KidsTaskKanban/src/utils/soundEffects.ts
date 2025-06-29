import Sound from 'react-native-sound';

Sound.setCategory('Playback');

const cringSound = new Sound('cring.mp3', Sound.MAIN_BUNDLE, (error) => {
  if (error) {
    console.log('failed to load the sound', error);
    return;
  }
  // loaded successfully
  console.log('duration in seconds: ' + cringSound.getDuration() + 'number of channels: ' + cringSound.getNumberOfChannels());
});

export const playCringSound = () => {
  cringSound.play((success) => {
    if (success) {
      console.log('successfully finished playing');
    } else {
      console.log('playback failed due to audio decoding errors');
    }
  });
};
